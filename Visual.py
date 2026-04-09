import pandas as pd
import requests

# ==========================
# CONFIGURAÇÕES
# ==========================
CAMINHO_ARQUIVO = r"C:\Users\User\OneDrive\Documents\SCORE CONTABILIDADE\03 - CONSULTORIA\Maria Lima Brand - 01-23\AGENTE DE IA\BASE DE CONHECIMENTO\PLANILHA BASE\fluxo_caixa_consolidado.xlsx"

WEBHOOK_URL = "https://score1.app.n8n.cloud/webhook-test/resumir-financeiro"


# ==========================
# NORMALIZAR TEXTO
# ==========================
def normalizar(texto):
    return (
        str(texto)
        .strip()
        .upper()
        .encode("ascii", errors="ignore")
        .decode("utf-8")
    )


# ==========================
# FILTRAR DADOS
# ==========================
def filtrar_dados(df, mes):
    if 'MES' not in df.columns:
        raise ValueError("Coluna 'MES' não encontrada.")

    df['MES'] = df['MES'].apply(normalizar)

    df_filtrado = df[df['MES'] == normalizar(mes)]

    return df_filtrado


# ==========================
# ENVIAR PARA WEBHOOK
# ==========================
def enviar_webhook(df_filtrado):
    dados = df_filtrado.to_dict(orient='records')

    response = requests.post(
        WEBHOOK_URL,
        json={"dados": dados},
        timeout=60
    )

    return response.status_code, response.text


# ==========================
# PROCESSO PRINCIPAL
# ==========================
def executar(mes_usuario):
    print("Lendo planilha consolidada...")

    df = pd.read_excel(CAMINHO_ARQUIVO)

    print("Filtrando dados...")
    df_filtrado = filtrar_dados(df, mes_usuario)

    print(f"Total de linhas filtradas: {len(df_filtrado)}")

    print("Enviando para webhook...")
    status, resposta = enviar_webhook(df_filtrado)

    print(f"Status: {status}")
    print(f"Resposta: {resposta}")


# ==========================
# EXECUÇÃO
# ==========================
if __name__ == "__main__":
    mes = input("Digite o mês (ex: MARCO): ")
    executar(mes)