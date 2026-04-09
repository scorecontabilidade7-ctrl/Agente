import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Chat Financeiro IA", layout="centered")

# =========================
# CONFIGURAÇÃO
# =========================
N8N_WEBHOOK_URL = "https://score1.app.n8n.cloud/webhook-test/resumir-financeiro"
ARQUIVO_EXCEL = r"C:\Users\User\OneDrive\Documents\SCORE CONTABILIDADE\03 - CONSULTORIA\Maria Lima Brand - 01-23\AGENTE DE IA\BASE DE CONHECIMENTO\PLANILHA BASE\fluxo_caixa_consolidado.xlsx"

# =========================
# ESTADO INICIAL
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "loading" not in st.session_state:
    st.session_state.loading = False

if "mes_escolhido" not in st.session_state:
    st.session_state.mes_escolhido = "JANEIRO"

if "dados_filtrados" not in st.session_state:
    st.session_state.dados_filtrados = []


def add_user_message(text):
    st.session_state.messages.append({
        "role": "user",
        "content": text
    })


def add_assistant_message(text):
    st.session_state.messages.append({
        "role": "assistant",
        "content": text
    })


def enviar_para_n8n(pergunta):
    """
    Envia a pergunta para o webhook do n8n
    e retorna o texto da resposta.
    """
    payload = {
        "message": pergunta,
        "mes": st.session_state.mes_escolhido,
        "dados": st.session_state.dados_filtrados
    }

    response = requests.post(
        N8N_WEBHOOK_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    # Ajuste aqui conforme o JSON que o n8n retornar
    return data.get("resposta", "O agente respondeu, mas não veio nenhum texto em 'resposta'.")


st.title("Chat Financeiro IA")

st.session_state.mes_escolhido = st.selectbox(
    "Selecione o mês",
    ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"],
    index=["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"].index(st.session_state.mes_escolhido)
)

df = pd.read_excel(ARQUIVO_EXCEL)
df.columns = [str(col).strip().upper() for col in df.columns]

if "MÊS" in df.columns:
    coluna_mes = "MÊS"
elif "MES" in df.columns:
    coluna_mes = "MES"
else:
    st.error("A planilha precisa ter uma coluna chamada 'MÊS' ou 'MES'.")
    st.stop()

df[coluna_mes] = df[coluna_mes].astype(str).str.strip().str.upper()
df_filtrado = df[df[coluna_mes] == st.session_state.mes_escolhido].copy()
st.session_state.dados_filtrados = df_filtrado.fillna("").to_dict(orient="records")

# =========================
# BOTÃO INICIAL
# =========================
col1, col2 = st.columns([1, 2])

with col1:
    if st.button("Resumir meu financeiro", use_container_width=True):
        pergunta = "Resuma meu financeiro"

        add_user_message(pergunta)
        st.session_state.loading = True
        st.rerun()

# =========================
# EXIBIÇÃO DO CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# CHAMADA AO N8N COM EFEITO DE 'PENSANDO'
# =========================
if st.session_state.loading:
    with st.chat_message("assistant"):
        with st.spinner("Pensando e consultando o agente de IA..."):
            try:
                ultima_pergunta = st.session_state.messages[-1]["content"]
                resposta_ia = enviar_para_n8n(ultima_pergunta)
                add_assistant_message(resposta_ia)

            except requests.exceptions.RequestException as e:
                add_assistant_message(f"Erro ao conectar com o n8n: {e}")

            except Exception as e:
                add_assistant_message(f"Ocorreu um erro inesperado: {e}")

            finally:
                st.session_state.loading = False
                st.rerun()