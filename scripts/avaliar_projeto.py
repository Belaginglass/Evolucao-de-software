#!/usr/bin/env python3
"""
Etapa 12 - sequência obrigatória de avaliação para uma versão (V0 a V10).

1. mvn clean package           -> compilacao.txt
2. mvn test                    -> testes_junit.csv (parseado de target/surefire-reports)
3. mvn verify (cobertura)      -> cobertura/ (cópia de target/site/jacoco)
4. mvn sonar:sonar             -> relatorios/sonarqube_measures.json
5. CK                          -> relatorios/ck/*.csv
6. consolidação                -> metricas.csv (uma linha por métrica, N/A quando aplicável)

Uso:
  python scripts/avaliar_projeto.py --versao V1
  python scripts/avaliar_projeto.py --versao V1 --sonar-token SEU_TOKEN
  python scripts/avaliar_projeto.py --versao V1 --sem-sonar   (pula SonarQube)
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROJETO_DIR = ROOT / "Projeto"
RESULTADOS_DIR = ROOT / "resultados"
CK_JAR = PROJETO_DIR / "tools" / "ck-0.7.0-jar-with-dependencies.jar"
SONAR_HOST = "http://localhost:9000"
SONAR_PROJECT_KEY = "dogtech"
NO_WINDOWS = os.name == "nt"


def erro(msg):
    print(f"ERRO: {msg}", file=sys.stderr)


def run(cmd, cwd=None, timeout=600):
    # No Windows, mvn é mvn.cmd: subprocess sem shell=True não resolve .cmd via PATH.
    return subprocess.run(cmd, cwd=cwd or PROJETO_DIR, capture_output=True,
                           text=True, encoding="utf-8", timeout=timeout, shell=NO_WINDOWS)


def git(*args):
    return subprocess.run(["git", *args], cwd=PROJETO_DIR, capture_output=True,
                           text=True, encoding="utf-8")


def resetar_banco():
    # Cada versão é avaliada a partir de um esquema limpo. Sem isto, o Hibernate
    # (ddl-auto=update) tenta ALTER TABLE incremental sobre o .db deixado por uma
    # versão anterior — e o SQLite não aceita ALTER TABLE ... ADD COLUMN UNIQUE
    # (erro real encontrado em V2: "Cannot add a UNIQUE column"). Isto é uma
    # decisão de ambiente/pipeline, não uma correção no código gerado.
    for db in (PROJETO_DIR / "data").glob("*.db"):
        db.unlink()


def etapa_compilacao(dir_versao: Path) -> bool:
    resetar_banco()
    r = run(["mvn", "-q", "clean", "package"])
    sucesso = r.returncode == 0
    texto = f"Resultado: {'Sucesso' if sucesso else 'Falha'}\n\n"
    if not sucesso:
        texto += "----- stdout -----\n" + r.stdout[-8000:] + "\n----- stderr -----\n" + r.stderr[-8000:]
    (dir_versao / "compilacao.txt").write_text(texto, encoding="utf-8")
    print(f"Compilação: {'SUCESSO' if sucesso else 'FALHA'} (ver {dir_versao / 'compilacao.txt'})")
    return sucesso


def etapa_testes(dir_versao: Path) -> dict:
    r = run(["mvn", "-q", "test"])
    reports_dir = PROJETO_DIR / "target" / "surefire-reports"
    linhas = []
    total = aprovados = reprovados = erros_count = pulados = 0
    if reports_dir.exists():
        for xml_file in sorted(reports_dir.glob("TEST-*.xml")):
            tree = ET.parse(xml_file)
            for tc in tree.getroot().findall("testcase"):
                classe = tc.get("classname")
                nome = tc.get("name")
                tempo = tc.get("time")
                falha = tc.find("failure")
                erro_el = tc.find("error")
                pulado = tc.find("skipped")
                total += 1
                if falha is not None:
                    status, msg = "Reprovado", (falha.get("message") or "")[:500]
                    reprovados += 1
                elif erro_el is not None:
                    status, msg = "Reprovado", (erro_el.get("message") or "")[:500]
                    erros_count += 1
                elif pulado is not None:
                    status, msg = "Não executado", "skipped"
                    pulados += 1
                else:
                    status, msg = "Aprovado", ""
                    aprovados += 1
                linhas.append([classe, nome, status, tempo, msg])
    with open(dir_versao / "testes_junit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["classe", "metodo", "situacao", "tempo_s", "mensagem_erro"])
        w.writerows(linhas)
    resumo = {"total": total, "aprovados": aprovados, "reprovados": reprovados + erros_count,
              "nao_executados": pulados, "mvn_test_exit_code": r.returncode}
    print(f"Testes JUnit: {resumo}")
    if r.returncode != 0 and total == 0:
        (dir_versao / "testes_junit_stderr.txt").write_text(r.stdout[-8000:] + r.stderr[-8000:], encoding="utf-8")
        erro("mvn test falhou antes de gerar relatórios (ver testes_junit_stderr.txt) — "
             "provavelmente erro de compilação dos próprios testes.")
    return resumo


def etapa_cobertura(dir_versao: Path):
    run(["mvn", "-q", "verify"])
    origem = PROJETO_DIR / "target" / "site" / "jacoco"
    destino = dir_versao / "cobertura"
    if origem.exists():
        if destino.exists():
            shutil.rmtree(destino)
        shutil.copytree(origem, destino)
        print(f"Cobertura copiada para {destino}")
    else:
        print("AVISO: target/site/jacoco não encontrado — cobertura indisponível (N/A), não 0%.")


def etapa_sonarqube(dir_versao: Path, versao: str, token: str):
    if not token:
        print("Sem token de SonarQube: etapa de análise estática pulada "
              "(métricas correspondentes ficam 'Não coletado' em metricas.csv).")
        return None
    # Sem "-q": precisamos do log do scanner para extrair o ceTaskUrl/ceTaskId e
    # esperar o processamento terminar — sem isso, a análise é assíncrona no
    # servidor e /api/measures/component pode devolver os números da versão
    # ANTERIOR (observado de fato na primeira execução real deste script em V1:
    # vieram os números de V0, porque a leitura ocorreu antes do processamento).
    r = run(["mvn", "sonar:sonar",
             f"-Dsonar.host.url={SONAR_HOST}", f"-Dsonar.token={token}",
             f"-Dsonar.projectKey={SONAR_PROJECT_KEY}", "-Dsonar.projectName=DogTech - SGA (TCC)",
             f"-Dsonar.projectVersion={versao}"], timeout=600)
    if r.returncode != 0:
        erro(f"mvn sonar:sonar falhou:\n{r.stderr[-4000:]}")
        return None

    m = re.search(r"api/ce/task\?id=(\S+)", r.stdout)
    if not m:
        erro("não encontrei o ceTaskUrl no log do scanner — seguindo sem esperar "
             "o processamento (métricas podem ficar desatualizadas).")
    else:
        task_id = m.group(1)
        status = None
        for _ in range(60):
            resp_task = requests.get(f"{SONAR_HOST}/api/ce/task", params={"id": task_id},
                                      headers={"Authorization": f"Bearer {token}"}, timeout=30)
            status = resp_task.json().get("task", {}).get("status") if resp_task.ok else None
            if status in ("SUCCESS", "FAILED", "CANCELED"):
                break
            time.sleep(2)
        if status != "SUCCESS":
            erro(f"task de análise do SonarQube terminou com status '{status}' "
                 f"(esperado SUCCESS) — métricas podem estar incompletas/desatualizadas.")

    metricas = ("ncloc,complexity,cognitive_complexity,duplicated_lines_density,"
                "code_smells,bugs,vulnerabilities,sqale_index,coverage,classes,functions")
    resp = requests.get(f"{SONAR_HOST}/api/measures/component",
                         params={"component": SONAR_PROJECT_KEY, "metricKeys": metricas},
                         headers={"Authorization": f"Bearer {token}"}, timeout=60)
    dados = resp.json() if resp.ok else {"erro_http": resp.status_code, "corpo": resp.text}
    (dir_versao / "relatorios").mkdir(parents=True, exist_ok=True)
    (dir_versao / "relatorios" / "sonarqube_measures.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SonarQube: medidas salvas em {dir_versao / 'relatorios' / 'sonarqube_measures.json'}")
    return dados


def etapa_ck(dir_versao: Path):
    if not CK_JAR.exists():
        print(f"AVISO: {CK_JAR} não encontrado — métricas CK ficam 'Não coletado'.")
        return
    destino = dir_versao / "relatorios" / "ck"
    destino.mkdir(parents=True, exist_ok=True)
    r = run(["java", "-jar", str(CK_JAR), str(PROJETO_DIR / "src"), "false", "0", "true",
             str(destino) + "/"], timeout=300)
    if r.returncode != 0:
        erro(f"CK falhou:\n{r.stderr[-2000:]}")
    else:
        print(f"CK: métricas salvas em {destino}")


def extrair_sonar_valor(dados, metric_key):
    if not dados or "component" not in dados:
        return None
    for m in dados["component"].get("measures", []):
        if m["metric"] == metric_key:
            return m["value"]
    return None


def montar_metricas_csv(dir_versao: Path, versao: str, sonar_dados, resumo_testes: dict):
    linhas = [
        ["metrica", "valor", "situacao", "justificativa"],
    ]

    def add_sonar(nome_metrica, key):
        valor = extrair_sonar_valor(sonar_dados, key)
        if sonar_dados is None:
            linhas.append([nome_metrica, "", "Não coletado", "SonarQube não executado nesta versão (sem token ou etapa pulada)"])
        elif valor is None:
            linhas.append([nome_metrica, "", "N/A", f"SonarQube não retornou o campo '{key}' para esta versão"])
        else:
            linhas.append([nome_metrica, valor, "Coletado", ""])

    add_sonar("LOC (ncloc)", "ncloc")
    add_sonar("Complexidade ciclomática", "complexity")
    add_sonar("Complexidade cognitiva", "cognitive_complexity")
    add_sonar("Duplicação (duplicated_lines_density %)", "duplicated_lines_density")
    add_sonar("Code smells", "code_smells")
    add_sonar("Cobertura (coverage %)", "coverage")

    ck_class_csv = dir_versao / "relatorios" / "ck" / "class.csv"
    if ck_class_csv.exists():
        with open(ck_class_csv, newline="", encoding="utf-8") as f:
            linhas_ck = list(csv.DictReader(f))
        if linhas_ck:
            wmc = sum(float(l["wmc"]) for l in linhas_ck)
            cbo = sum(float(l["cbo"]) for l in linhas_ck) / len(linhas_ck)
            lcom_vals = [float(l["lcom"]) for l in linhas_ck if l["lcom"] not in ("", "NaN")]
            lcom = sum(lcom_vals) / len(lcom_vals) if lcom_vals else None
            linhas.append(["WMC (soma por classe)", round(wmc, 2), "Coletado", f"{len(linhas_ck)} classes analisadas pelo CK"])
            linhas.append(["CBO (média por classe)", round(cbo, 2), "Coletado", ""])
            if lcom is not None:
                linhas.append(["LCOM (média por classe)", round(lcom, 2), "Coletado", ""])
            else:
                linhas.append(["LCOM (média por classe)", "", "N/A", "CK retornou NaN para LCOM em todas as classes (classes com <2 métodos)"])
        else:
            linhas.append(["WMC/CBO/LCOM", "", "N/A", "CK não encontrou nenhuma classe em Projeto/src"])
    else:
        linhas.append(["WMC/CBO/LCOM", "", "Não coletado", "CK não foi executado nesta versão"])

    linhas.append(["Testes executados", resumo_testes.get("total", ""), "Coletado", ""])
    linhas.append(["Testes aprovados", resumo_testes.get("aprovados", ""), "Coletado", ""])
    linhas.append(["Testes reprovados", resumo_testes.get("reprovados", ""), "Coletado", ""])

    executados = resumo_testes.get("aprovados", 0) + resumo_testes.get("reprovados", 0)
    # Auxiliar: taxa de aprovação da suíte JUnit "crua" (como o Gemini escreveu os testes).
    # NÃO é a TA oficial da etapa 7.3/12.3 (essa é por caso de teste funcional CTxxx,
    # em testes/casos_teste.xlsx -> aba "Suíte Acumulativa"; ver registrar_resultados.py).
    if executados == 0:
        linhas.append(["Taxa de aprovação (testes JUnit automatizados — auxiliar)", "", "Não calculável", "nenhum teste JUnit aprovado ou reprovado nesta versão"])
    else:
        ta = round(resumo_testes["aprovados"] / executados * 100, 1)
        linhas.append(["Taxa de aprovação (testes JUnit automatizados — auxiliar)", ta, "Coletado", ""])

    with open(dir_versao / "metricas.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(linhas)
    print(f"metricas.csv consolidado em {dir_versao / 'metricas.csv'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--versao", required=True, help="Ex.: V0, V1, ..., V10")
    ap.add_argument("--sonar-token", default=None)
    ap.add_argument("--sem-sonar", action="store_true")
    ap.add_argument("--sem-ck", action="store_true")
    args = ap.parse_args()

    dir_versao = RESULTADOS_DIR / args.versao
    dir_versao.mkdir(parents=True, exist_ok=True)

    sucesso_compilacao = etapa_compilacao(dir_versao)
    resumo_testes = etapa_testes(dir_versao) if sucesso_compilacao else {"total": 0, "aprovados": 0, "reprovados": 0, "nao_executados": 0}
    if sucesso_compilacao:
        etapa_cobertura(dir_versao)
    sonar_dados = None
    if sucesso_compilacao and not args.sem_sonar:
        sonar_dados = etapa_sonarqube(dir_versao, args.versao, args.sonar_token)
    if sucesso_compilacao and not args.sem_ck:
        etapa_ck(dir_versao)

    montar_metricas_csv(dir_versao, args.versao, sonar_dados, resumo_testes)
    print(f"\nAvaliação de {args.versao} concluída. Resultados em {dir_versao}")


if __name__ == "__main__":
    main()
