import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

load_dotenv()

st.set_page_config(
    page_title="LedgerMind AI - Financial Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stChatFloatingInputContainer {
        background-color: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
    }
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_headers=True)

@st.cache_data
def load_data():
    transactions = pd.read_csv("data/transacoes.csv")
    history = pd.read_csv("data/historico_atendimento.csv")
    with open("data/perfil_investidor.json", "r") as f:
        profile = json.load(f)
    with open("data/produtos_financeiros.json", "r") as f:
        products = json.load(f)
    return transactions, history, profile, products

transactions, history, profile, products = load_data()

with st.sidebar:
    st.title("📊 LedgerMind Dashboard")
    st.markdown("---")
    st.subheader("Client Profile")
    st.write(f"**Name:** {profile.get('nome', 'N/A')}")
    st.write(f"**Profile:** {profile.get('perfil', 'N/A')}")
    
    st.subheader("Recent Activity")
    st.dataframe(transactions.tail(5), hide_index=True)
    
    total_spent = transactions['valor'].sum()
    st.metric("Total Transactions", f"R$ {total_spent:,.2f}")

def get_agent():

    context = f"""
    Client Profile: {json.dumps(profile)}
    Available Products: {json.dumps(products)}
    Recent Transactions: {transactions.tail(10).to_string()}
    """
    
    return Agent(
        name="LedgerMind",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "Você é o LedgerMind, um assistente financeiro de IA especializado em análise de despesas e planejamento proativo.",
            "TONALIDADE: Educativo, direto, consultivo e profissional.",
            "REGRAS CRÍTICAS:",
            "1. Use EXCLUSIVAMENTE os dados fornecidos no contexto (Transações, Perfil, Histórico).",
            "2. Se a informação não estiver na base, responda: 'Não encontrei dados suficientes nos meus registros atuais para responder com precisão.'",
            "3. NUNCA invente números, datas ou produtos.",
            "4. Não solicite ou compartilhe senhas ou dados sensíveis.",
            "5. Sempre verifique o perfil do investidor antes de sugerir produtos.",
            f"CONTEXTO DO CLIENTE: {context}"
        ],
        markdown=True
    )

st.title("🤖 LedgerMind Conversational Agent")
st.caption("How can I help you with your financial planning today?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Qual foi meu maior gasto este mês?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent = get_agent()
        response = agent.run(prompt)
        st.markdown(response.content)
        st.session_state.messages.append({"role": "assistant", "content": response.content})
