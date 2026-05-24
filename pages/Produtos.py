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
    #url = st.secrets["supabase"]["url"]
    #key = st.secrets["supabase"]["key"]
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

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
# Criamos as chaves que os próprios inputs usarão diretamente como 'key'
if "id_cliente" not in st.session_state:
    st.session_state.id_cliente = None
if "txt_nome" not in st.session_state:
    st.session_state.txt_nome = ""
if "txt_email" not in st.session_state:
    st.session_state.txt_email = ""
if "sb_estado" not in st.session_state:
    st.session_state.sb_estado = lista_estados[0] if lista_estados else ""


# Função para limpar o formulário
def limpar_formulario():
    st.session_state.id_cliente = None
    st.session_state.txt_nome = ""
    st.session_state.txt_email = ""
    st.session_state.sb_estado = lista_estados[0] if lista_estados else ""


# -----------------------------------------------------------------------------
# Interface Principal: Divide a tela em duas colunas (Formulário e Tabela)
# -----------------------------------------------------------------------------
col_form, col_tabela = st.columns([1, 2])

with col_form:
    st.subheader("📝 Formulário do Cliente")

    # Identifica se estamos editando ou criando
    if st.session_state.id_cliente:
        st.info(f"Editando Cliente ID: {st.session_state.id_cliente}")
    else:
        st.success("Criando Novo Cliente")

    # ATENÇÃO: Vinculamos direto usando 'key'. Não usamos o parâmetro 'value'.
    # Isso destrava os campos completamente para digitação e seleção livre.
    nome = st.text_input("Nome", key="txt_nome")
    email = st.text_input("Email", key="txt_email")
    estado = st.selectbox("Estado", options=lista_estados, key="sb_estado")

    # Botões de Ação (C, U, D)
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("Salvar / Gravar", type="primary", use_container_width=True):
            if nome and email:
                dados = {"nome": nome, "email": email, "estado_sigla": estado}

                if st.session_state.id_cliente:
                    # UPDATE
                    supabase.table("clientes").update(dados).eq("id", st.session_state.id_cliente).execute()
                    st.toast("Cliente atualizado com sucesso!")
                else:
                    # CREATE
                    supabase.table("clientes").insert(dados).execute()
                    st.toast("Cliente cadastrado com sucesso!")

                limpar_formulario()
                st.rerun()
            else:
                st.error("Preencha Nome e Email!")

    with col_btn2:
        if st.session_state.id_cliente:
            if st.button("❌ Deletar", type="secondary", use_container_width=True):
                # DELETE
                supabase.table("clientes").delete().eq("id", st.session_state.id_cliente).execute()
                st.toast("Cliente removido!")
                limpar_formulario()
                st.rerun()

    with col_btn3:
        if st.button("Limpar", use_container_width=True):
            limpar_formulario()
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

        # Verifica se o usuário selecionou uma linha na tabela
        if evento_selecao and "rows" in evento_selecao["selection"] and len(evento_selecao["selection"]["rows"]) > 0:
            idx_linha_clicada = evento_selecao["selection"]["rows"][0]
            dados_cliente = df_clientes.iloc[idx_linha_clicada]

            # Força a atualização do formulário APENAS se o ID clicado for diferente do atual
            if st.session_state.id_cliente != int(dados_cliente["id"]):
                st.session_state.id_cliente = int(dados_cliente["id"])
                st.session_state.txt_nome = str(dados_cliente["nome"])
                st.session_state.txt_email = str(dados_cliente["email"])
                st.session_state.sb_estado = str(dados_cliente["estado_sigla"])
                st.rerun()
    else:
        st.info("Nenhum cliente cadastrado ainda.")