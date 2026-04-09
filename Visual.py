import streamlit as st
import requests

st.set_page_config(page_title="Chat Financeiro IA", layout="centered")

# =========================
# CONFIGURAÇÃO
# =========================
N8N_WEBHOOK_URL = "https://score1.app.n8n.cloud/webhook/resumir-financeiro"

# =========================
# ESTADO INICIAL
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "loading" not in st.session_state:
    st.session_state.loading = False

if "chat_liberado" not in st.session_state:
    st.session_state.chat_liberado = False

if "mes_escolhido" not in st.session_state:
    st.session_state.mes_escolhido = "JANEIRO"


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


def enviar_para_n8n(pergunta, mes):
    """
    Envia a pergunta para o webhook do n8n
    e retorna o texto da resposta.
    """
    payload = {
        "message": pergunta,
        "mes": mes
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

mes = st.selectbox(
    "Selecione o mês",
    [
        "JANEIRO",
        "FEVEREIRO",
        "MARÇO",
        "ABRIL",
        "MAIO",
        "JUNHO",
        "JULHO",
        "AGOSTO",
        "SETEMBRO",
        "OUTUBRO",
        "NOVEMBRO",
        "DEZEMBRO"
    ],
    index=[
        "JANEIRO",
        "FEVEREIRO",
        "MARÇO",
        "ABRIL",
        "MAIO",
        "JUNHO",
        "JULHO",
        "AGOSTO",
        "SETEMBRO",
        "OUTUBRO",
        "NOVEMBRO",
        "DEZEMBRO"
    ].index(st.session_state.mes_escolhido)
)

st.session_state.mes_escolhido = mes

# =========================
# BOTÃO INICIAL
# =========================
col1, col2 = st.columns([1, 2])

with col1:
    if st.button("Resumir meu financeiro", use_container_width=True):
        pergunta = "Resuma meu financeiro"

        add_user_message(pergunta)
        st.session_state.loading = True
        st.session_state.chat_liberado = True
        st.rerun()

# =========================
# EXIBIÇÃO DO CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# ENTRADA DE NOVAS PERGUNTAS
# =========================
if st.session_state.chat_liberado and not st.session_state.loading:
    pergunta_usuario = st.chat_input("Digite sua pergunta sobre o financeiro")
    if pergunta_usuario:
        add_user_message(pergunta_usuario)
        st.session_state.loading = True
        st.rerun()

# =========================
# CHAMADA AO N8N COM EFEITO DE 'PENSANDO'
# =========================
if st.session_state.loading:
    with st.chat_message("assistant"):
        with st.spinner("Consultando Fluxo de Caixa"):
            try:
                ultima_pergunta = st.session_state.messages[-1]["content"]
                resposta_ia = enviar_para_n8n(ultima_pergunta, st.session_state.mes_escolhido)
                add_assistant_message(resposta_ia)

            except requests.exceptions.RequestException as e:
                add_assistant_message(f"Erro ao conectar com o n8n: {e}")

            except Exception as e:
                add_assistant_message(f"Ocorreu um erro inesperado: {e}")

            finally:
                st.session_state.loading = False
                st.rerun()