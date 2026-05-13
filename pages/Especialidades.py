import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Cadastrar", page_icon="📂")
st.title("📂 Cadastrar Produto")

# Conexão
conn = st.connection("supabase_connection", type=SupabaseConnection)

with st.form("cadastro_form", clear_on_submit=True):
    codigo = st.text_input("Codigo")
    razao = st.number_input("Razão")
    submit = st.form_submit_button("Cadastrar")

    if submit:
        # Inserção
        conn.table("clinicas").insert({"codigo": codigo, "razao": razao}).execute()
        st.success("Clinica cadastrado com sucesso!")