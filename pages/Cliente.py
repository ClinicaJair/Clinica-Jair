import streamlit as st
from supabase import create_client

# Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("👤 Cadastro de Clientes")

# Formulário para cadastrar
with st.form("form_cliente"):
    nome = st.text_input("Nome do Cliente")
    email = st.text_input("Email")
    submit = st.form_submit_button("Cadastrar")

    if submit:
        # Inserir no PostgreSQL
        supabase.table("clientes").insert({"nome": nome, "email": email}).execute()
        st.success(f"Cliente {nome} cadastrado!")

# Listar clientes
st.subheader("Clientes Cadastrados")
response = supabase.table("clientes").select("*").execute()
st.dataframe(response.data)
