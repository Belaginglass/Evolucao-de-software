#!/usr/bin/env python3
"""
Etapas 8-10 (passos 1-9) - chamada ao Gemini para gerar um incremento do DogTech e
aplicar as alterações resultantes.

Formato de saída (decisão revista após 2 tentativas reais com unified diff falharem
por erro de contagem de linhas nos cabeçalhos de hunk — ver
resultados/V1/tentativas/tentativa_01 e tentativa_02): o Gemini responde com um JSON
{"arquivos": [{"caminho", "acao", "conteudo"}, ...]} — caminho+conteúdo completo de
cada arquivo, sem diffs. Mais robusto para aplicação automática: não depende de
contexto de linha exato.

Fluxo:
  1. Confere que o Projeto/ está limpo e no commit esperado (versão anterior).
  2. Monta o prompt (prompt-base + Apêndice C + requisitos do incremento + prompt
     específico do incremento + arquivos atuais).
  3. Envia ao Gemini (modelo e parâmetros fixos).
  4. Recebe a resposta, extrai o JSON de arquivos.
  5. Valida TODOS os caminhos (dentro de Projeto/src ou pom.xml, sem escapar do
     projeto) antes de escrever QUALQUER arquivo (tudo ou nada).
  6. Escreve os arquivos; gera um diff real via `git diff` (calculado pelo git, não
     pelo modelo) só para registro legível.
  7. Preserva TODA tentativa (sucesso ou falha) em
     resultados/V<n>/tentativas/tentativa_NN/, e copia os artefatos da tentativa
     que deu certo para resultados/V<n>/.

Uso:
  python scripts/gerar_codigo.py --incremento I1
  python scripts/gerar_codigo.py --incremento I1 --dry-run
  python scripts/gerar_codigo.py --incremento I1 --force
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
PROJETO_DIR = ROOT / "Projeto"
PROMPTS_DIR = ROOT / "prompts"
REQUISITOS_DIR = ROOT / "requisitos"
RESULTADOS_DIR = ROOT / "resultados"

MODELO_PADRAO = "gemini-3.5-flash-lite"
TEMPERATURE_PADRAO = 0.0

EXTENSOES_TEXTO = {".java", ".xml", ".properties", ".yml", ".yaml", ".html", ".csv",
                   ".sql", ".md", ".txt", ".gitignore"}
DIRETORIOS_IGNORADOS = {"target", "tools", ".git", ".idea", ".vscode", "data"}
PREFIXOS_PERMITIDOS = ("src/", "pom.xml")

RESTRICOES_E_CRITERIOS = """\
RESTRIÇÕES E CRITÉRIOS DE CONCLUSÃO DA RESPOSTA
- Responda com um ÚNICO bloco de código ```json contendo exatamente este formato,
  e nada além disso dentro do bloco:
  {
    "arquivos": [
      {"caminho": "src/main/java/com/tcc/iterativa/.../Foo.java",
       "acao": "criar" | "modificar" | "remover",
       "conteudo": "<conteúdo TEXTUAL COMPLETO do arquivo, já com o resultado final;"
                   " omitido/vazio quando acao=remover>"}
    ]
  }
- "caminho" é relativo à raiz do projeto Spring Boot (Projeto/), com barras "/",
  nunca ".." nem caminho absoluto. Deve começar LITERALMENTE com "src/" (incluindo
  "src/main/java/" para código Java — nunca omita esse prefixo) ou ser exatamente
  "pom.xml" — não modifique nenhum outro arquivo.
  Exemplo de "caminho" CORRETO para uma classe nova no pacote config (string única,
  sem quebra de linha): "src/main/java/com/tcc/iterativa/config/Exemplo.java"
  Exemplo INCORRETO (NÃO faça isso — falta o prefixo "src/main/java/"):
  "com/tcc/iterativa/config/Exemplo.java"
- "conteudo" é o arquivo INTEIRO já modificado (não um diff, não um trecho) — para
  "modificar", repita também as partes que não mudaram.
- CRÍTICO — "conteudo" precisa ser uma string JSON válida: todo caractere de aspas
  duplas (") que apareça DENTRO do código (ex.: um literal String do Java como
  @Table(name = "usuarios"), ou um atributo HTML como title="texto") DEVE ser
  escapado como \" no JSON. Toda quebra de linha deve ser \n (não uma quebra de
  linha literal). Todo backslash deve ser \\. Isso é o erro mais comum — revise
  mentalmente cada "conteudo" antes de responder, caractere por caractere nas
  aspas, procurando aspas internas não escapadas.
  Exemplo CORRETO (trecho de "conteudo" de um arquivo Java, dentro do JSON):
  "conteudo": "@Table(name = \"usuarios\")\npublic class Usuario {\n..."
  Exemplo INCORRETO (quebra o JSON — NÃO faça isso):
  "conteudo": "@Table(name = "usuarios")\npublic class Usuario {\n..."
- Não gere um unified diff. Não inclua texto explicativo dentro do bloco ```json```.
  Qualquer observação, suposição ou lista de requisitos atendidos deve vir DEPOIS do
  bloco, em texto normal.
- Ao final, fora do bloco de código, liste: (a) arquivos criados/modificados/
  removidos; (b) os identificadores de requisitos atendidos (RF/RNF/RN); (c)
  suposições feitas.
"""


def erro(msg):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def ler(caminho: Path) -> str:
    if not caminho.exists():
        erro(f"arquivo esperado não encontrado: {caminho}")
    return caminho.read_text(encoding="utf-8")


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=PROJETO_DIR, capture_output=True,
                           text=True, encoding="utf-8", check=check)


def git_status_limpo() -> bool:
    return git("status", "--short", check=False).stdout.strip() == ""


def git_head() -> str:
    r = git("rev-parse", "HEAD", check=False)
    return r.stdout.strip() if r.returncode == 0 else "(sem commits)"


def git_head_subject() -> str:
    r = git("log", "-1", "--format=%s", check=False)
    return r.stdout.strip() if r.returncode == 0 else ""


def coletar_arquivos_projeto() -> str:
    partes = []
    candidatos = [PROJETO_DIR / "pom.xml"]
    for caminho in sorted((PROJETO_DIR / "src").rglob("*")):
        if caminho.is_dir():
            continue
        if any(p in DIRETORIOS_IGNORADOS for p in caminho.relative_to(PROJETO_DIR).parts):
            continue
        candidatos.append(caminho)
    for caminho in candidatos:
        if caminho.suffix.lower() not in EXTENSOES_TEXTO and caminho.name != ".gitignore":
            continue
        rel = caminho.relative_to(PROJETO_DIR).as_posix()
        conteudo = caminho.read_text(encoding="utf-8")
        partes.append(f"===== ARQUIVO: {rel} =====\n{conteudo}\n")
    return "\n".join(partes)


def montar_prompt(incremento: str) -> str:
    prompt_base = ler(PROMPTS_DIR / "prompt_base.txt")
    apendice_c = ler(REQUISITOS_DIR / "apendice_c_esclarecimentos.md")
    requisitos_incremento = ler(REQUISITOS_DIR / "incrementos" / f"{incremento}.md")
    prompt_incremento_path = PROMPTS_DIR / f"{incremento}.txt"
    if not prompt_incremento_path.exists():
        erro(f"{prompt_incremento_path} não existe — crie o prompt específico do "
             f"incremento {incremento} antes de rodar este script.")
    prompt_incremento = ler(prompt_incremento_path)
    estado_projeto = coletar_arquivos_projeto()

    return f"""{prompt_base}

===== APÊNDICE C — ESCLARECIMENTOS E DECISÕES DE INTERPRETAÇÃO =====
{apendice_c}

===== REQUISITOS DO INCREMENTO {incremento} =====
{requisitos_incremento}

===== PROMPT ESPECÍFICO DO INCREMENTO {incremento} =====
{prompt_incremento}

===== ESTADO ATUAL DO PROJETO (Projeto/) =====
{estado_projeto}

===== {RESTRICOES_E_CRITERIOS.splitlines()[0]} =====
{RESTRICOES_E_CRITERIOS}
"""


def montar_prompt_correcao(incremento: str, erro_texto: str) -> str:
    estado_projeto = coletar_arquivos_projeto()
    return f"""Você gerou o código abaixo para o incremento {incremento} do DogTech em uma
chamada anterior. Ao compilar com `mvn clean package`, o seguinte erro ocorreu:

===== ERRO DE COMPILAÇÃO =====
{erro_texto}

===== ESTADO ATUAL DO PROJETO (Projeto/, já com o erro) =====
{estado_projeto}

Corrija APENAS o necessário para o projeto compilar. Não altere comportamento,
não adicione funcionalidades novas, não modifique arquivos que não precisam de
correção para este erro específico.

{RESTRICOES_E_CRITERIOS}
"""


def ocultar_chave(texto: str, api_key: str) -> str:
    return texto.replace(api_key, "***REDACTED***") if api_key else texto


def chamar_gemini(prompt: str, modelo: str, temperature: float, api_key: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    t0 = time.monotonic()
    try:
        resp = requests.post(url, params={"key": api_key}, json=payload, timeout=300)
    except requests.RequestException as e:
        raise requests.RequestException(ocultar_chave(str(e), api_key)) from None
    tempo_resposta = time.monotonic() - t0
    try:
        resp.raise_for_status()
    except requests.RequestException as e:
        raise requests.RequestException(ocultar_chave(str(e), api_key)) from None
    data = resp.json()
    texto = "".join(
        p.get("text", "")
        for c in data.get("candidates", [])
        for p in c.get("content", {}).get("parts", [])
    )
    uso = data.get("usageMetadata", {})
    finish_reason = (data.get("candidates") or [{}])[0].get("finishReason")
    return texto, uso, finish_reason, tempo_resposta


def extrair_json_arquivos(resposta: str):
    m = re.search(r"```json\s*\n(.*?)```", resposta, re.DOTALL)
    bruto = m.group(1).strip() if m else resposta.strip()
    try:
        # strict=False: aceita caracteres de controle literais (ex.: '\n' não escapado)
        # dentro de strings — comum quando o modelo embute código-fonte multilinha num
        # valor JSON sem escapar as quebras de linha. Isso só afeta o que o PARSER
        # aceita como JSON válido; não altera nem reinterpreta o conteúdo em si.
        dados = json.loads(bruto, strict=False)
    except json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"
    arquivos = dados.get("arquivos")
    if not isinstance(arquivos, list) or not arquivos:
        return None, "JSON não contém uma lista não vazia em 'arquivos'"
    for item in arquivos:
        if not isinstance(item, dict) or "caminho" not in item or "acao" not in item:
            return None, f"item malformado em 'arquivos': {item!r}"
        if item["acao"] not in ("criar", "modificar", "remover"):
            return None, f"acao inválida: {item.get('acao')!r} (caminho={item.get('caminho')!r})"
    return arquivos, None


def validar_caminhos(arquivos):
    for item in arquivos:
        caminho = item["caminho"]
        if caminho.startswith("/") or ".." in Path(caminho).parts:
            return f"caminho não permitido (absoluto ou com '..'): {caminho}"
        if not caminho.startswith(PREFIXOS_PERMITIDOS):
            return f"caminho fora de src/ e diferente de pom.xml: {caminho}"
        destino = (PROJETO_DIR / caminho).resolve()
        if PROJETO_DIR.resolve() not in destino.parents and destino != PROJETO_DIR.resolve():
            return f"caminho resolve para fora de Projeto/: {caminho}"
        if item["acao"] == "remover" and not destino.exists():
            return f"acao=remover para arquivo que não existe: {caminho}"
        if item["acao"] in ("criar", "modificar") and "conteudo" not in item:
            return f"acao={item['acao']} sem 'conteudo': {caminho}"
    return None


def normalizar_quebras_linha(texto: str) -> str:
    # O modelo às vezes embute "\r\n" (CRLF) literal dentro do valor JSON. Em
    # modo texto no Windows, write_text traduz '\n' -> os.linesep (CRLF) e
    # read_text traduz de volta — mas um CRLF já presente na string vira
    # "\r" + "\r\n" na escrita, e a leitura universal-newlines conta isso como
    # DOIS fins de linha, duplicando-os. Normalizar para só "\n" antes de
    # escrever evita essa duplicação e deixa o arquivo com final de linha
    # consistente (LF), o que não afeta nada no Java/Maven.
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def escrever_arquivos(arquivos):
    for item in arquivos:
        destino = PROJETO_DIR / item["caminho"]
        if item["acao"] == "remover":
            destino.unlink()
        else:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(normalizar_quebras_linha(item["conteudo"]), encoding="utf-8")


def verificar_integridade(arquivos) -> list:
    problemas = []
    for item in arquivos:
        destino = PROJETO_DIR / item["caminho"]
        if item["acao"] == "remover":
            if destino.exists():
                problemas.append(f"{item['caminho']}: deveria ter sido removido mas ainda existe")
        else:
            if not destino.exists():
                problemas.append(f"{item['caminho']}: deveria existir mas não foi encontrado após a escrita")
            elif destino.read_text(encoding="utf-8") != normalizar_quebras_linha(item["conteudo"]):
                problemas.append(f"{item['caminho']}: conteúdo gravado difere do conteúdo enviado")
    return problemas


def proxima_tentativa(dir_tentativas: Path) -> int:
    dir_tentativas.mkdir(parents=True, exist_ok=True)
    existentes = [int(p.name.split("_")[1]) for p in dir_tentativas.glob("tentativa_*") if p.is_dir()]
    return max(existentes, default=0) + 1


def stage_tudo():
    # `git diff` (sem --cached) nunca mostra arquivos untracked — arquivos novos
    # escritos por escrever_arquivos() não apareceriam no relatório sem isto.
    # `git add -A` só move para o índice (staged); não cria commit.
    git("add", "-A", check=False)


def arquivos_alterados_desde(commit_base: str) -> str:
    stage_tudo()
    r = git("diff", "--cached", "--name-status", commit_base, check=False)
    rotulos = {"A": "Criado", "M": "Modificado", "D": "Removido", "R": "Renomeado"}
    linhas = []
    for linha in r.stdout.splitlines():
        if not linha.strip():
            continue
        partes = linha.split("\t")
        status, caminho = partes[0], partes[-1]
        rotulo = rotulos.get(status[0], status)
        linhas.append(f"{rotulo}\t{caminho}")
    return "\n".join(linhas) if linhas else "(nenhum arquivo alterado)"


def diff_real_desde(commit_base: str) -> str:
    """Diff calculado pelo git após a escrita dos arquivos — não gerado pelo
    modelo. Usado só como registro legível, nunca como mecanismo de aplicação.
    Requer stage_tudo() já ter sido chamado (feito em arquivos_alterados_desde)."""
    r = git("diff", "--cached", commit_base, check=False)
    return r.stdout


def salvar_metadados(caminho: Path, metadados: dict):
    caminho.write_text(json.dumps(metadados, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--incremento", required=True, help="Ex.: I1, I2, ..., I10")
    ap.add_argument("--dry-run", action="store_true", help="Monta e mostra o prompt, mas não chama a API")
    ap.add_argument("--force", action="store_true", help="Ignora working tree sujo e commit-base inesperado")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--temperature", type=float, default=TEMPERATURE_PADRAO)
    ap.add_argument("--corrigir", action="store_true",
                     help="Modo de correção: envia o erro de compilação/teste (de "
                          "resultados/V<n>/compilacao.txt, ou --erro) + estado atual "
                          "(já com o defeito) e pede uma correção mínima, em vez de "
                          "montar o prompt completo do incremento do zero.")
    ap.add_argument("--erro", default=None, help="Texto do erro a corrigir (sobrepõe compilacao.txt)")
    args = ap.parse_args()

    incremento = args.incremento.upper()
    if not re.fullmatch(r"I(10|[1-9])", incremento):
        erro("--incremento deve ser I1 a I10")
    numero = int(incremento[1:])
    versao_anterior = f"V{numero - 1}"
    versao_resultante = f"V{numero}"

    if args.corrigir:
        erro_texto = args.erro
        if erro_texto is None:
            compilacao_path = RESULTADOS_DIR / versao_resultante / "compilacao.txt"
            if not compilacao_path.exists():
                erro(f"--corrigir sem --erro precisa de {compilacao_path} (rode "
                     f"scripts/avaliar_projeto.py --versao {versao_resultante} primeiro).")
            erro_texto = compilacao_path.read_text(encoding="utf-8")
    else:
        if not args.force and not git_status_limpo():
            erro("Projeto/ tem alterações não commitadas. Commite ou descarte antes de "
                 "gerar um novo incremento (ou use --force, por sua conta e risco).")

    subject = git_head_subject()
    if not args.force and subject and not subject.startswith(versao_anterior):
        erro(f"o commit HEAD atual ('{subject}') não começa com '{versao_anterior}' — "
             f"{incremento} deveria partir de {versao_anterior}. Use --force se isso for intencional.")

    commit_base = git_head()
    dir_versao = RESULTADOS_DIR / versao_resultante
    dir_tentativas = dir_versao / "tentativas"
    n_tentativa = proxima_tentativa(dir_tentativas)
    dir_tentativa = dir_tentativas / f"tentativa_{n_tentativa:02d}"
    dir_tentativa.mkdir(parents=True, exist_ok=True)

    prompt = montar_prompt_correcao(incremento, erro_texto) if args.corrigir else montar_prompt(incremento)
    (dir_tentativa / "prompt.txt").write_text(prompt, encoding="utf-8")
    print(f"[{incremento} -> {versao_resultante}, tentativa {n_tentativa}{' (correção)' if args.corrigir else ''}] "
          f"Prompt montado ({len(prompt)} caracteres). Commit base: {commit_base}")

    if args.dry_run:
        print("--dry-run: nenhuma chamada à API foi feita.")
        return

    env = dotenv_values(PROJETO_DIR / ".env")
    api_key = env.get("GEMINI_API_KEY")
    if not api_key:
        erro("GEMINI_API_KEY não encontrada em Projeto/.env")

    id_execucao = f"{incremento}-t{n_tentativa:02d}-{uuid.uuid4().hex[:8]}"
    metadados = {
        "id_execucao": id_execucao,
        "incremento": incremento,
        "versao_anterior": versao_anterior,
        "versao_resultante": versao_resultante,
        "tentativa": n_tentativa,
        "tipo": "correcao" if args.corrigir else "geracao",
        "modelo": args.modelo,
        "parametros": {
            "temperature": args.temperature,
            "top_p": None,
            "top_k": None,
            "nota_parametros": "top_p/top_k não fixados explicitamente: com temperature=0 a "
                                "amostragem é determinística (greedy), tornando-os irrelevantes "
                                "para o resultado; não estimados nem inventados.",
        },
        "formato_resposta": "json (caminho+conteúdo completo) — não unified diff "
                             "(ver docstring do script para o motivo da mudança)",
        "data_hora_inicio": datetime.now(timezone.utc).isoformat(),
        "commit_base": commit_base,
    }

    try:
        resposta, uso, finish_reason, tempo_resposta = chamar_gemini(
            prompt, args.modelo, args.temperature, api_key)
    except requests.RequestException as e:
        metadados.update({
            "data_hora_fim": datetime.now(timezone.utc).isoformat(),
            "sucesso_chamada": False,
            "erros": [f"chamada à API falhou: {e}"],
        })
        salvar_metadados(dir_tentativa / "metadados.json", metadados)
        erro(f"chamada à API falhou (registrado em {dir_tentativa}): {e}")
        return

    metadados.update({
        "data_hora_fim": datetime.now(timezone.utc).isoformat(),
        "tempo_resposta_segundos": round(tempo_resposta, 3),
        "sucesso_chamada": True,
        "finish_reason": finish_reason,
        "tokens_entrada": uso.get("promptTokenCount"),
        "tokens_saida": uso.get("candidatesTokenCount"),
        "tokens_total": uso.get("totalTokenCount"),
        "erros": [],
    })
    (dir_tentativa / "resposta_gemini.txt").write_text(resposta, encoding="utf-8")
    print(f"Resposta recebida em {metadados['tempo_resposta_segundos']}s "
          f"({metadados['tokens_entrada']} tokens entrada / "
          f"{metadados['tokens_saida']} tokens saída). finishReason={finish_reason}")

    arquivos, motivo_falha = extrair_json_arquivos(resposta)
    if arquivos is None:
        metadados["json_extraido"] = False
        metadados["alteracoes_aplicadas"] = False
        metadados["erros"].append(motivo_falha)
        salvar_metadados(dir_tentativa / "metadados.json", metadados)
        erro(f"resposta inválida: {motivo_falha}. Nada foi aplicado. "
             f"Tentativa preservada em {dir_tentativa} para revisão manual.")
        return
    metadados["json_extraido"] = True
    metadados["arquivos_na_resposta"] = [{"caminho": a["caminho"], "acao": a["acao"]} for a in arquivos]

    erro_validacao = validar_caminhos(arquivos)
    if erro_validacao:
        metadados["alteracoes_aplicadas"] = False
        metadados["erros"].append(f"validação de caminhos falhou: {erro_validacao}")
        salvar_metadados(dir_tentativa / "metadados.json", metadados)
        erro(f"validação de caminhos falhou: {erro_validacao}\n"
             f"NENHUM arquivo foi escrito (tudo ou nada). Tentativa preservada em {dir_tentativa}.")
        return

    escrever_arquivos(arquivos)
    problemas = verificar_integridade(arquivos)
    if problemas:
        metadados["alteracoes_aplicadas"] = False
        metadados["erros"].extend(problemas)
        salvar_metadados(dir_tentativa / "metadados.json", metadados)
        erro("verificação de integridade pós-escrita falhou:\n" + "\n".join(problemas) +
             f"\nTentativa preservada em {dir_tentativa}. Revise manualmente antes de prosseguir "
             "(os arquivos já foram escritos; considere reverter com git checkout/clean).")
        return

    metadados["alteracoes_aplicadas"] = True
    arquivos_txt = arquivos_alterados_desde(commit_base)
    diff_legivel = diff_real_desde(commit_base)
    (dir_tentativa / "arquivos_alterados.txt").write_text(arquivos_txt, encoding="utf-8")
    (dir_tentativa / "patch.patch").write_text(diff_legivel, encoding="utf-8")
    metadados["arquivos_alterados"] = arquivos_txt.splitlines()
    salvar_metadados(dir_tentativa / "metadados.json", metadados)

    for nome in ("prompt.txt", "resposta_gemini.txt", "patch.patch", "metadados.json", "arquivos_alterados.txt"):
        shutil.copy2(dir_tentativa / nome, dir_versao / nome)

    print(f"Alterações aplicadas com sucesso em {PROJETO_DIR}.")
    print(f"Artefatos da tentativa {n_tentativa} em {dir_tentativa}")
    print(f"Artefatos da tentativa vencedora copiados para {dir_versao}")
    print("Arquivos alterados:")
    print(arquivos_txt)
    print("\nPróximo passo: rodar scripts/avaliar_projeto.py --versao " + versao_resultante)


if __name__ == "__main__":
    main()
