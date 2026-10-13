from datetime import datetime
import io
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from supabase import Client, create_client

# 1. Configuração da página
st.set_page_config(page_title="Sistema Comercial", page_icon="📊", layout="wide")

# 2. Conexão com o Banco de Dados
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# CABEÇALHO (Sem loop automático)
# =========================================================
col_topo1, col_topo2 = st.columns([3, 1])

with col_topo1:
    st.title("🏥 Clínica Dr. Jair")
    st.caption("Painel Administrativo - Visão Completa")

with col_topo2:
    # Exibição da data e hora atual (estática ao carregar)
    agora = datetime.now()
    data_formatada = agora.strftime("%d/%m/%Y")
    hora_formatada = agora.strftime("%H:%M:%S")

    st.markdown(
        f"""
        <div style="text-align: right; padding: 5px; background-color: #f0f2f6; border-radius: 8px;">
            <span style="font-size: 13px; font-weight: bold;">🕒 {data_formatada} - {hora_formatada}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# =========================================================
# CONTEÚDO PRINCIPAL (Página Única / Seções Sequenciais)
# =========================================================

# 1. Dashboard
st.header("🚀 Dashboard de Gestão")

# Consulta no Supabase
resultado_paciente = supabase.table("pacientes").select("*").execute()
qtd_paciente = (
    resultado_paciente.count
    if resultado_paciente.count is not None
    else 0
)

col1, col2, col3 = st.columns(3)
col1.metric("Pacientes Cadastrados", qtd_paciente, "+5")
col2.metric("Médicos Cadastrados", "01", "12")
col3.metric("Especialidades", "R$ 15.000", "+12%")

st.markdown("---")

# 2. Gestão de Pacientes
st.subheader("👥 Gestão de Pacientes")
st.write("Conteúdo da tela de cadastro e edição de pacientes.")

st.markdown("---")

# 3. Gestão de Médicos
st.subheader("🩺 Gestão de Médicos")
st.write("Conteúdo da tela de cadastro e edição de médicos.")

st.markdown("---")

# 4. Fichas Médicas
st.subheader("📋 Fichas Médicas")
st.write("Conteúdo da gestão de fichas médicas.")

st.markdown("---")

# 5. Agendamentos
st.subheader("📅 Agendamentos de Consultas")
st.write("Conteúdo do controle da agenda de consultas.")

st.markdown("---")

# 6. Relatórios
st.subheader("📊 Relatórios do Sistema")
st.write("Conteúdo para geração e exportação de relatórios.")