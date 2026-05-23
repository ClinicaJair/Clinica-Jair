import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Configuração da Conexão com Supabase
# É recomendado usar st.secrets no Streamlit para segurança
#SUPABASE_URL = "SUA_URL_SUPABASE"
#SUPABASE_KEY = "SUA_CHAVE_SUPABASE"
SUPABASE_URL = "https://lcruodkgvahvyijbgbch.supabase.co"
SUPABASE_KEY = "sb_publishable_2dK9DdBevblDyz5ZhYtyaQ_6E0woJsZ"

def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()


# 2. Funções do Banco de Dados (CRUD)
def read_customers():
    response = supabase.table("clientes").select("*").execute()
    return pd.DataFrame(response.data)


def create_customer(nome, email, telefone):
    supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
    st.success("Cliente cadastrado com sucesso!")


def update_customer(cliente_id, nome, email, telefone):
    supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id", cliente_id).execute()
    st.success("Cliente atualizado com sucesso!")


def delete_customer(cliente_id):
    supabase.table("clientes").delete().eq("id", cliente_id).execute()
    st.success("Cliente deletado com sucesso!")


# 3. Layout da Interface (Formulário e DataFrame)
st.title("Cadastro de Clientes - CRUD Supabase")

# Estado da Sessão para guardar o ID do cliente selecionado
if 'selected_customer_id' not in st.session_state:
    st.session_state.selected_customer_id = None

# Ler dados atuais
df_clientes = read_customers()

# Aba 1: Formulário (Create / Update / Delete)
with st.container():
    st.subheader("Gerenciar Cliente")

    # Se um cliente foi clicado no dataframe, preenche o formulário
    # (Trata caso o df esteja vazio ou sem seleção)
    default_nome, default_email, default_telefone = "", "", ""

    if st.session_state.selected_customer_id is not None:
        cliente_selecionado = df_clientes[df_clientes['id'] == st.session_state.selected_customer_id]
        if not cliente_selecionado.empty:
            default_nome = cliente_selecionado.iloc[0]['nome']
            default_email = cliente_selecionado.iloc[0]['email']
            default_telefone = cliente_selecionado.iloc[0]['telefone']

    with st.form(key="cliente_form"):
        nome = st.text_input("Nome", value=default_nome)
        email = st.text_input("E-mail", value=default_email)
        telefone = st.text_input("Telefone", value=default_telefone)

        # Botões de ação
        col1, col2, col3 = st.columns(3)
        with col1:
            btn_create = st.form_submit_button("Cadastrar (Create)")
        with col2:
            btn_update = st.form_submit_button("Salvar Alterações (Update)")
        with col3:
            btn_delete = st.form_submit_button("Deletar (Delete)")

    if btn_create:
        create_customer(nome, email, telefone)
        st.rerun()

    if btn_update:
        if st.session_state.selected_customer_id is not None:
            update_customer(st.session_state.selected_customer_id, nome, email, telefone)
            st.rerun()
        else:
            st.warning("Selecione um cliente primeiro para atualizar.")

    if btn_delete:
        if st.session_state.selected_customer_id is not None:
            delete_customer(st.session_state.selected_customer_id)
            st.session_state.selected_customer_id = None
            st.rerun()
        else:
            st.warning("Selecione um cliente primeiro para deletar.")

# Aba 2: Exibição dos dados e Seleção Interativa
st.subheader("Lista de Clientes")

if not df_clientes.empty:
    # Seleção nativa de linhas do Streamlit (on_select="rerun" para atualizar a tela)
    event = st.dataframe(
        df_clientes,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Ao clicar em uma linha, atualiza o session_state e recarrega a tela
    if event.selection.rows:
        selected_index = event.selection.rows[0]
        st.session_state.selected_customer_id = df_clientes.iloc[selected_index]['id']
else:
    st.info("Nenhum cliente cadastrado ainda.")
