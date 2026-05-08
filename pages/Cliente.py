import streamlit as st
from supabase import create_client

# Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("👤 Cadastro da Clinica")

# Formulário para cadastrar
with st.form("form_clinica"):
    codigo = st.text_input("Codigo")
    razao = st.text_input("Razão Social")
    fantasia = st.text_input("Nome Fantasia")
    endereco = st.text_input("Endereço")
    cep = st.text_input("CEP")
    bairro = st.text_input("Bairro")
    cidade = st.text_input("Cidade")
    estado = st.text_input("Estado")
    telefone = st.text_input("Telefone")
    telefone1 = st.text_input("Telefone1")
    cnpj = st.text_input("CNPJ")
    inscricao = st.text_input("Inscrição Estadual")
    data_fundacao = st.text_input("Data de Fundação")
    email = st.text_input("E-mail")
    site = st.text_input("Site")
    stragram = st.text_input("Stagram")
    submit = st.form_submit_button("Cadastrar")

    if submit:
        # Inserir no PostgreSQL
        supabase.table("clinicas").insert({"Razão Social": razao, "Nome Fantasia": fantasia,"Telefone": telefone }).execute()
        st.success(f"Clinica {razao} cadastrado!")

# Listar clientes
st.subheader("Clinicas Cadastrados")
response = supabase.table("clinicas").select("*").execute()
st.dataframe(response.data)
