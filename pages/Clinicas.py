import streamlit as st
from supabase import create_client

# Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 1. Configurar a página (opcional, mas recomendado)
st.set_page_config(layout="wide")

# 2. CSS para remover o espaçamento do topo
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

st.title("👤 Cadastro da Clinica")

with st.form("form_clinica"):

    #st.write("Insira os dados abaixo:")

    # 1. Definir proporções (ex: 20% / 80%)
    col1, col2, col3, col4 = st.columns([1,7,4,2])
    col5, col6 = st.columns([5,3])
    col7, col8, col9 = st.columns([1,6,3])
    col10, col11, = st.columns([4,1])
    col12, col13 = st.columns([2,6])
    col14, col15, col16 = st.columns([3,3,3])

    # 2. Usar 'with' para adicionar widgets nas colunas
    with col1:
        codigo = st.text_input("Codigo")

    with col2:
        razao = st.text_input("Razão Social")

    with col3:
        fantasia = st.text_input("Nome Fantasia")

    with col4:
        data_fundacao = st.text_input("Data de Fundação")

    with col5:
        cnpj = st.text_input("CNPJ")

    with col6:
        inscricao = st.text_input("Inscrição Estadual")

    #st.divider()

    with col7:
        cep = st.text_input("CEP")

    with col8:
        endereco = st.text_input("Endereço")

    with col9:
        bairro = st.text_input("Bairro")

    with col10:
        cidade = st.text_input("Cidade")

    with col11:
        estado = st.text_input("Estado")

    with col12:
        telefone = st.text_input("Telefone")

    with col13:
        telefone1 = st.text_input("Telefone1")

    with col14:
        email = st.text_input("E-mail")

    with col15:
        site = st.text_input("Site")

    with col16:
        instagram = st.text_input("Instagram")


# Formulário para cadastrar
#with st.form("form_clinica"):
#    codigo = st.text_input("Codigo")
#    razao = st.text_input("Razão Social")
#    fantasia = st.text_input("Nome Fantasia")
#    endereco = st.text_input("Endereço")
#    cep = st.text_input("CEP")
#    bairro = st.text_input("Bairro")
#    cidade = st.text_input("Cidade")
#    estado = st.text_input("Estado")
#    telefone = st.text_input("Telefone")
#    telefone1 = st.text_input("Telefone1")
#    cnpj = st.text_input("CNPJ")
#    inscricao = st.text_input("Inscrição Estadual")
#    data_fundacao = st.text_input("Data de Fundação")
#    email = st.text_input("E-mail")
#    site = st.text_input("Site")
#    instagram = st.text_input("Instagram")
    submit = st.form_submit_button("Cadastrar")

if submit:
    # Inserir no PostgreSQL
    supabase.table("clinicas").insert({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
                                       "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado, "telefone": telefone,
                                       "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
                                       "data_fundacao": data_fundacao, "email": email, "site": site, "instagram": instagram}).execute()
    st.success(f"Clinica {razao} cadastrado!")

# Listar clientes
st.subheader("Clinicas Cadastrados")
response = supabase.table("clinicas").select("*").execute()
st.dataframe(response.data)
