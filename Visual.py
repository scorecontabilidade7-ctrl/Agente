import os
import pandas as pd
import requests
from openpyxl import load_workbook

# ==========================
# CONFIGURAÇÕES
# ==========================
ARQUIVO_SAIDA = r"C:\Users\User\OneDrive\Documents\SCORE CONTABILIDADE\03 - CONSULTORIA\Maria Lima Brand - 01-23\AGENTE DE IA\BASE DE CONHECIMENTO\PLANILHA BASE\fluxo_caixa_consolidado.xlsx"

WEBHOOK_URL = "https://score1.app.n8n.cloud/webhook-test/resumir-financeiro"

LINHA_CABECALHO = 1
EXTENSOES_VALIDAS = (".xlsx", ".xlsm", ".xls")
ABA_ALVO = None


# ==========================
# FUNÇÕES (MANTIDAS)
# ==========================
def limpar_linhas_vazias(df):
    return df.dropna(how="all").reset_index(drop=True)


def normalizar(texto):
    return (
        str(texto)
        .strip()
        .upper()
        .encode("ascii", errors="ignore")
        .decode("utf-8")
    )


def filtrar_dados(df, mes):
    df = df.copy()

    if 'MES' not in df.columns:
        raise ValueError("A coluna 'MES' não foi encontrada na planilha.")

    df['MES'] = df['MES'].apply(normalizar)

    df_filtrado = df[df['MES'] == normalizar(mes)]

    return df_filtrado


def enviar_webhook(df_filtrado):
    dados = df_filtrado.to_dict(orient='records')

    response = requests.post(
        WEBHOOK_URL,
        json={"dados": dados},
        timeout=60
    )

    return response.status_code, response.text


# ==========================
# PROCESSAMENTO PRINCIPAL
# ==========================
def consolidar_planilhas(mes_usuario):
    print("Lendo arquivo consolidado...")

    df_final = pd.read_excel(ARQUIVO_SAIDA)

    df_final = limpar_linhas_vazias(df_final)

    # ==========================
    # FILTRAR POR MÊS
    # ==========================
    df_filtrado = filtrar_dados(df_final, mes_usuario)

    print(f"\nTotal de linhas filtradas: {len(df_filtrado)}")

    # ==========================
    # ENVIAR PARA WEBHOOK
    # ==========================
    status, resposta = enviar_webhook(df_filtrado)

    print(f"\nStatus webhook: {status}")
    print(f"Resposta: {resposta}")


# ==========================
# EXECUÇÃO
# ==========================
if __name__ == "__main__":
    mes = input("Digite o mês (ex: MARCO): ")
    consolidar_planilhas(mes)