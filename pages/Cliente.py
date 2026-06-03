import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Clientes")

# Conexão com Supabase usando os secrets do Streamlit
url = st.secrets["supabase"]["supabase_url"]
key = st.secrets["supabase"]["supabase_key"]
supabase = create_client(url, key)

st.title("Cadastro de Clientes")

menu = ["Cadastrar", "Consultar/Editar/Excluir"]
choice = st.sidebar.selectbox("Ação", menu)

# --- CREATE ---
if choice == "Cadastrar":
    st.subheader("Adicionar Novo Cliente")
    with st.form("form_cliente"):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone")
        submit = st.form_submit_button("Salvar Cliente")

        if submit:
            if nome and email:
                data = supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
                st.success(f"Cliente {nome} cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha nome e e-mail.")

# --- READ, UPDATE E DELETE ---
elif choice == "Consultar/Editar/Excluir":
    st.subheader("Clientes Cadastrados")
    response = supabase.table("clientes").select("*").execute()
    clientes = response.data

    for c in clientes:
        with st.expander(f"{c['nome']} - {c['email']}"):
            with st.form(f"form_edit_{c['id']}"):
                novo_nome = st.text_input("Nome", value=c['nome'])
                novo_email = st.text_input("E-mail", value=c['email'])
                novo_tel = st.text_input("Telefone", value=c['telefone'])

                editar = st.form_submit_button("Salvar Alterações")
                deletar = st.form_submit_button("Excluir Cliente")

                if editar:
                    supabase.table("clientes").update({"nome": novo_nome, "email": novo_email, "telefone": novo_tel}).eq("id",
                                                                                                                         c['id']).execute()
                    st.success("Dados atualizados!")
                    st.rerun()
                if deletar:
                    supabase.table("clientes").delete().eq("id", c['id']).execute()
                    st.success("Cliente excluído!")
                    st.rerun()
