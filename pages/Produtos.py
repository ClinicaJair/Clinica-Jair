import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração da página
st.set_page_config(page_title="CRUD Clientes Supabase", layout="wide")
st.title("👥 Cadastro de Clientes (CRUD)")


# -----------------------------------------------------------------------------
# Conexão com o Supabase
# -----------------------------------------------------------------------------
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


supabase: Client = init_connection()


# -----------------------------------------------------------------------------
# Funções Auxiliares de Banco de Dados
# -----------------------------------------------------------------------------
def buscar_estados():
    res = supabase.table("estados").select("sigla, nome").execute()
    return pd.DataFrame(res.data)


def buscar_clientes():
    res = supabase.table("clientes").select("id, nome, email, estado_sigla").execute()
    return pd.DataFrame(res.data)


# Carrega os estados do banco
df_estados = buscar_estados()
lista_estados = df_estados["sigla"].tolist() if not df_estados.empty else []

# -----------------------------------------------------------------------------
# Inicialização do Estado da Tela (Session State)
# -----------------------------------------------------------------------------
if "cliente_id" not in st.session_state:
    st.session_state.cliente_id = None
if "nome_input" not in st.session_state:
    st.session_state.nome_input = ""
if "email_input" not in st.session_state:
    st.session_state.email_input = ""
if "estado_input" not in st.session_state:
    st.session_state.estado_input = lista_estados[0] if lista_estados else ""


# -----------------------------------------------------------------------------
# Callbacks para atualizar o estado sem travar a UI
# -----------------------------------------------------------------------------
def atualizar_estado_selecionado():
    # Sincroniza o valor escolhido no selectbox de volta para a nossa variável de controle
    st.session_state.estado_input = st.session_state.sb_estado


# -----------------------------------------------------------------------------
# Interface Principal: Divide a tela em duas colunas (Formulário e Tabela)
# -----------------------------------------------------------------------------
col_form, col_tabela = st.columns([1, 2])

with col_form:
    st.subheader("📝 Formulário do Cliente")

    # Identifica se estamos editando ou criando
    if st.session_state.cliente_id:
        st.info(f"Editando Cliente ID: {st.session_state.cliente_id}")
    else:
        st.success("Criando Novo Cliente")

    # Inputs de texto vinculados ao session_state via variável
    nome = st.text_input("Nome", value=st.session_state.nome_input)
    email = st.text_input("Email", value=st.session_state.email_input)

    # Tratamento do índice do Selectbox
    if st.session_state.estado_input in lista_estados:
        idx_estado = lista_estados.index(st.session_state.estado_input)
    else:
        idx_estado = 0

    # O segredo: usamos o 'key' e o 'on_change' para processar a mudança imediatamente
    estado = st.selectbox(
        "Estado",
        options=lista_estados,
        index=idx_estado,
        key="sb_estado",
        on_change=atualizar_estado_selecionado
    )

    # Botões de Ação (C, U, D)
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("Salvar / Gravar", type="primary", use_container_width=True):
            if nome and email:
                dados = {"nome": nome, "email": email, "estado_sigla": st.session_state.estado_input}

                if st.session_state.cliente_id:
                    # UPDATE
                    supabase.table("clientes").update(dados).eq("id", st.session_state.cliente_id).execute()
                    st.toast("Cliente atualizado com sucesso!")
                else:
                    # CREATE
                    supabase.table("clientes").insert(dados).execute()
                    st.toast("Cliente cadastrado com sucesso!")

                # Reseta tudo após salvar
                st.session_state.cliente_id = None
                st.session_state.nome_input = ""
                st.session_state.email_input = ""
                st.session_state.estado_input = lista_estados[0] if lista_estados else ""
                st.rerun()
            else:
                st.error("Preencha Nome e Email!")

    with col_btn2:
        if st.session_state.cliente_id:
            if st.button("❌ Deletar", type="secondary", use_container_width=True):
                # DELETE
                supabase.table("clientes").delete().eq("id", st.session_state.cliente_id).execute()
                st.toast("Cliente removido!")

                # Reseta o formulário
                st.session_state.cliente_id = None
                st.session_state.nome_input = ""
                st.session_state.email_input = ""
                st.session_state.estado_input = lista_estados[0] if lista_estados else ""
                st.rerun()

    with col_btn3:
        if st.button("Limpar", use_container_width=True):
            st.session_state.cliente_id = None
            st.session_state.nome_input = ""
            st.session_state.email_input = ""
            st.session_state.estado_input = lista_estados[0] if lista_estados else ""
            st.rerun()

with col_tabela:
    st.subheader("📊 Clientes Cadastrados (READ)")
    st.write("Clique na linha para carregar os dados no formulário lateral:")

    df_clientes = buscar_clientes()

    if not df_clientes.empty:
        evento_selecao = st.dataframe(
            df_clientes,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Verifica se o usuário selecionou uma nova linha na tabela
        if evento_selecao and "rows" in evento_selecao["selection"] and len(evento_selecao["selection"]["rows"]) > 0:
            idx_linha_clicada = evento_selecao["selection"]["rows"][0]
            dados_cliente = df_clientes.iloc[idx_linha_clicada]

            # Atualiza o formulário apenas se mudou o ID selecionado
            if st.session_state.cliente_id != int(dados_cliente["id"]):
                st.session_state.cliente_id = int(dados_cliente["id"])
                st.session_state.nome_input = str(dados_cliente["nome"])
                st.session_state.email_input = str(dados_cliente["email"])
                st.session_state.estado_input = str(dados_cliente["estado_sigla"])
                st.rerun()
    else:
        st.info("Nenhum cliente cadastrado ainda.")