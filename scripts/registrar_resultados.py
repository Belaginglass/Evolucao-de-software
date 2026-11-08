#!/usr/bin/env python3
"""
Etapa 12.1/12.2/12.3 - consolida, entre todas as versões já avaliadas
(resultados/V0/ .. resultados/V10/), as três tabelas pedidas:

  resultados/consolidado/compilacao.csv     (12.1 - Versão | Compilação | Observação)
  resultados/consolidado/testes_regressao.csv (12.2 - Teste | V0 | V1 | ... )
  resultados/consolidado/metricas.csv       (12.3 - Métrica | V0 | V1 | ... )

Só lê o que já existe; versões ainda não avaliadas aparecem como "Não coletado".
Rode de novo após avaliar cada versão nova.

Uso:
  python scripts/registrar_resultados.py
"""
import csv
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
RESULTADOS_DIR = ROOT / "resultados"
CASOS_TESTE_XLSX = ROOT / "testes" / "casos_teste.xlsx"
CONSOLIDADO_DIR = RESULTADOS_DIR / "consolidado"

VERSOES = ["V0"] + [f"V{i}" for i in range(1, 11)]

METRICAS_12_3 = [
    ("LOC (ncloc)", "LOC (ncloc)"),
    ("Complexidade ciclomática", "Complexidade ciclomática"),
    ("WMC (soma por classe)", "WMC"),
    ("CBO (média por classe)", "CBO"),
    ("LCOM (média por classe)", "LCOM"),
    ("Complexidade cognitiva", "Complexidade cognitiva"),
    ("Duplicação (duplicated_lines_density %)", "Duplicação"),
    ("Code smells", "Code smells"),
]


def dir_versao(v):
    return RESULTADOS_DIR / v


def consolidar_compilacao():
    linhas = [["Versão", "Compilação", "Observação"]]
    for v in VERSOES:
        arq = dir_versao(v) / "compilacao.txt"
        obs_arq = dir_versao(v) / "observacoes.txt"
        if not arq.exists():
            linhas.append([v, "Não avaliado", ""])
            continue
        primeira_linha = arq.read_text(encoding="utf-8").splitlines()[0]
        resultado = primeira_linha.replace("Resultado: ", "").strip()
        obs = obs_arq.read_text(encoding="utf-8").strip() if obs_arq.exists() else ""
        linhas.append([v, resultado, obs])
    CONSOLIDADO_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONSOLIDADO_DIR / "compilacao.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(linhas)
    print(f"{CONSOLIDADO_DIR / 'compilacao.csv'} gerado.")


def consolidar_testes_regressao():
    if not CASOS_TESTE_XLSX.exists():
        print(f"AVISO: {CASOS_TESTE_XLSX} não encontrado — pulando matriz de regressão.")
        return
    wb = openpyxl.load_workbook(CASOS_TESTE_XLSX, data_only=True)
    ws_casos = wb["Casos de Teste"]
    ws_exec = wb["Execuções por Versão"]

    ids_ordenados = []
    for row in ws_casos.iter_rows(min_row=2, values_only=True):
        if row[0]:
            ids_ordenados.append(row[0])

    estado = {tid: {} for tid in ids_ordenados}
    for row in ws_exec.iter_rows(min_row=2, values_only=True):
        versao, test_id, _inc, situacao = row[0], row[1], row[2], row[3]
        if not versao or not test_id:
            continue
        estado.setdefault(test_id, {})[versao] = situacao or ""

    linhas = [["Teste"] + VERSOES]
    for tid in ids_ordenados:
        linha = [tid] + [estado.get(tid, {}).get(v, "—") for v in VERSOES]
        linhas.append(linha)

    CONSOLIDADO_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONSOLIDADO_DIR / "testes_regressao.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(linhas)
    print(f"{CONSOLIDADO_DIR / 'testes_regressao.csv'} gerado ({len(ids_ordenados)} casos).")


def consolidar_metricas():
    valores = {chave: {} for chave, _ in METRICAS_12_3}
    for v in VERSOES:
        arq = dir_versao(v) / "metricas.csv"
        if not arq.exists():
            for chave, _ in METRICAS_12_3:
                valores[chave][v] = "Não avaliado"
            continue
        with open(arq, newline="", encoding="utf-8") as f:
            linhas_csv = {l["metrica"]: l for l in csv.DictReader(f)}
        for chave, _ in METRICAS_12_3:
            registro = linhas_csv.get(chave)
            if registro is None:
                valores[chave][v] = "N/A"
            elif registro["situacao"] == "Coletado":
                valores[chave][v] = registro["valor"]
            else:
                valores[chave][v] = registro["situacao"]

    linhas = [["Métrica"] + VERSOES]
    for chave, rotulo in METRICAS_12_3:
        linhas.append([rotulo] + [valores[chave].get(v, "Não avaliado") for v in VERSOES])
    linhas.append(["Taxa de aprovação (TA)"] + ler_ta_oficial())

    CONSOLIDADO_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONSOLIDADO_DIR / "metricas.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(linhas)
    print(f"{CONSOLIDADO_DIR / 'metricas.csv'} gerado.")


def ler_ta_oficial():
    """TA oficial (etapa 7.3/12.3), calculada por caso de teste funcional (CTxxx) —
    não confundir com a taxa auxiliar de testes JUnit brutos salva em
    resultados/Vn/metricas.csv. Calculada aqui diretamente a partir das linhas de
    'Execuções por Versão' (não da coluna de fórmula da aba 'Suíte Acumulativa'):
    o openpyxl não recalcula fórmulas e este ambiente não tem LibreOffice para
    recalculá-las antes da leitura, então a fórmula ficaria com valor em cache
    vazio (None) — ler o dado bruto e recalcular em Python evita esse problema."""
    if not CASOS_TESTE_XLSX.exists():
        return ["Não avaliado"] * len(VERSOES)
    wb = openpyxl.load_workbook(CASOS_TESTE_XLSX, data_only=True)
    ws = wb["Execuções por Versão"]
    contagens = {v: {"Aprovado": 0, "Reprovado": 0} for v in VERSOES}
    for row in ws.iter_rows(min_row=2, values_only=True):
        versao, situacao = row[0], row[3]
        if versao in contagens and situacao in ("Aprovado", "Reprovado"):
            contagens[versao][situacao] += 1
    resultado = []
    for v in VERSOES:
        aprovados, reprovados = contagens[v]["Aprovado"], contagens[v]["Reprovado"]
        executados = aprovados + reprovados
        resultado.append("Não calculável" if executados == 0 else round(aprovados / executados * 100, 1))
    return resultado


if __name__ == "__main__":
    consolidar_compilacao()
    consolidar_testes_regressao()
    consolidar_metricas()
