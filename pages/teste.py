import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configurações do Supabase (Acesse suas Configurações -> API)
#SUPABASE_URL = "SUA_URL_AQUI"
#SUPABASE_KEY = "SUA_CHAVE_DE_API_AQUI"
SUPABASE_URL = "https://lcruodkgvahvyijbgbch.supabase.co"
SUPABASE_KEY = "sb_publishable_2dK9DdBevblDyz5ZhYtyaQ_6E0woJsZ"


# Inicializa a conexão com o Supabase
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase: Client = init_supabase()

st.set_page_config(page_title="Cadastro de Clientes", layout="wide")
st.title("💻 Cadastro de Clientes - Supabase + Streamlit")


# Funções de CRUD
def create_cliente(nome, email, telefone):
    data = supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
    return data


def read_clientes():
    response = supabase.table("clientes").select("*").execute()
    return pd.DataFrame(response.data)


def update_cliente(cliente_id, nome, email, telefone):
    data = supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id", cliente_id).execute()
    return data


def delete_cliente(cliente_id):
    data = supabase.table("clientes").delete().eq("id", cliente_id).execute()
    return data


# Variáveis de controle para limpar campos
def limpar_campos():
    st.session_state["id"] = ""
    st.session_state["nome"] = ""
    st.session_state["email"] = ""
    st.session_state["telefone"] = ""


# --- Layout da Tela ---
col1, col2 = st.columns([1, 2])

# Coluna 1: Formulário de Cadastro
with col1:
    st.subheader("Ficha do Cliente")

    # Inputs com valores do st.session_state (para conseguir limpar/preencher via código)
    cliente_id = st.text_input("ID do Cliente (Somente leitura)", key="id", disabled=True)
    nome = st.text_input("Nome", key="nome")
    email = st.text_input("E-mail", key="email")
    telefone = st.text_input("Telefone", key="telefone")

    # Botões Create, Update, Delete
    st.write("")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

    with c1:
        if st.button("➕ Cadastrar"):
            if nome and email:
                create_cliente(nome, email, telefone)
                st.success("Cadastrado!")
                st.rerun()
            else:
                st.warning("Preencha Nome e E-mail.")

    with c2:
        if st.button("🔄 Atualizar"):
            if cliente_id and nome and email:
                update_cliente(cliente_id, nome, email, telefone)
                st.success("Atualizado!")
                st.rerun()
            else:
                st.warning("Selecione um cliente e preencha os dados.")

    with c3:
        if st.button("🗑️ Deletar"):
            if cliente_id:
                delete_cliente(cliente_id)
                st.success("Deletado!")
                limpar_campos()
                st.rerun()
            else:
                st.warning("Selecione um cliente para deletar.")

    with c4:
        if st.button("🧹 Limpar"):
            limpar_campos()
            st.rerun()

# Coluna 2: DataFrame (Read)
with col2:
    st.subheader("Clientes Cadastrados")
    df = read_clientes()

    if not df.empty:
        # Exibe o DataFrame permitindo que o usuário clique em uma linha
        event = st.dataframe(
            df[['id', 'nome', 'email', 'telefone']],
            use_container_width=True,
            hide_index=True,
            on_select="rerun"
        )

        # Pega a linha clicada no dataframe e atualiza o session_state
        selection = event.selection.get("rows")
        if selection:
            linha_selecionada = selection[0]
            cliente_selecionado = df.iloc[linha_selecionada]

            st.session_state["id"] = cliente_selecionado["id"]
            st.session_state["nome"] = cliente_selecionado["nome"]
            st.session_state["email"] = cliente_selecionado["email"]
            st.session_state["telefone"] = cliente_selecionado["telefone"]
    else:
        st.info("Nenhum cliente cadastrado no banco de dados.")
