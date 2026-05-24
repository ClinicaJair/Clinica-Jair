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
# Funções de Banco de Dados
# -----------------------------------------------------------------------------
def buscar_estados():
    try:
        res = supabase.table("estados").select("sigla, nome").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Erro ao buscar estados: {e}")
        return pd.DataFrame(columns=["sigla", "nome"])


def buscar_clientes():
    try:
        res = supabase.table("clientes").select("id, nome, email, estado_sigla").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Erro ao buscar clientes: {e}")
        return pd.DataFrame(columns=["id", "nome", "email", "estado_sigla"])


# Carrega dados iniciais do banco
df_estados = buscar_estados()
lista_estados = df_estados["sigla"].tolist() if not df_estados.empty else []

# -----------------------------------------------------------------------------
# Inicialização das Variáveis de Controle de Estado (Session State)
# -----------------------------------------------------------------------------
if "id_selecionado" not in st.session_state:
    st.session_state.id_selecionado = None
if "val_nome" not in st.session_state:
    st.session_state.val_nome = ""
if "val_email" not in st.session_state:
    st.session_state.val_email = ""
if "val_estado" not in st.session_state:
    st.session_state.val_estado = lista_estados[0] if lista_estados else ""

# -----------------------------------------------------------------------------
# Layout de Duas Colunas
# -----------------------------------------------------------------------------
col_form, col_tabela = st.columns([1, 2])

# -----------------------------------------------------------------------------
# Coluna da Direita: DATAFRAME (READ) - Processado primeiro para capturar o clique
# -----------------------------------------------------------------------------
with col_tabela:
    st.subheader("📊 Clientes Cadastrados")
    st.caption("Clique na linha ou use a caixa de seleção para editar o registro:")

    df_clientes = buscar_clientes()

    if not df_clientes.empty:
        # Configuração estável e testada para captura de clique
        tabela_interativa = st.dataframe(
            df_clientes,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Captura exata da linha selecionada
        selecao = tabela_interativa.get("selection", {}).get("rows", [])
        if selecao:
            idx_linha = selecao[0]
            linha_dados = df_clientes.iloc[idx_linha]
            id_clicado = int(linha_dados["id"])

            # Executa apenas se o clique for em um ID diferente do atual em memória
            if st.session_state.id_selecionado != id_clicado:
                st.session_state.id_selecionado = id_clicado
                st.session_state.val_nome = str(linha_dados["nome"])
                st.session_state.val_email = str(linha_dados["email"])
                st.session_state.val_estado = str(linha_dados["estado_sigla"])
                st.rerun()
    else:
        st.info("Nenhum cliente encontrado no banco de dados.")

# -----------------------------------------------------------------------------
# Coluna da Esquerda: FORMULÁRIO (CREATE / UPDATE / DELETE)
# -----------------------------------------------------------------------------
with col_form:
    st.subheader("📝 Formulário do Cliente")

    if st.session_state.id_selecionado:
        st.info(f"Modo: Editando ID {st.session_state.id_selecionado}")
    else:
        st.success("Modo: Criando Novo Registro")

    # Truque do sufixo na Key: se mudamos de ID, o componente reseta visualmente.
    # Se mantemos o ID, ele permite digitação e seleção livre sem travar.
    sufixo_key = f"_{st.session_state.id_selecionado}" if st.session_state.id_selecionado else "_novo"

    nome_input = st.text_input("Nome", value=st.session_state.val_nome, key=f"nome{sufixo_key}")
    email_input = st.text_input("Email", value=st.session_state.val_email, key=f"email{sufixo_key}")

    # Tratamento do index do selectbox baseado no banco
    try:
        idx_estado = lista_estados.index(st.session_state.val_estado)
    except ValueError:
        idx_estado = 0

    estado_input = st.selectbox(
        "Estado",
        options=lista_estados,
        index=idx_estado,
        key=f"estado{sufixo_key}"
    )

    # Botões de Operação do CRUD
    st.write("")
    col_salvar, col_deletar, col_limpar = st.columns(3)

    with col_salvar:
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            if nome_input.strip() and email_input.strip():
                dados_payload = {
                    "nome": nome_input,
                    "email": email_input,
                    "estado_sigla": estado_input
                }

                if st.session_state.id_selecionado:
                    # UPDATE
                    supabase.table("clientes").update(dados_payload).eq("id", st.session_state.id_selecionado).execute()
                    st.toast("Cliente atualizado!")
                else:
                    # CREATE
                    supabase.table("clientes").insert(dados_payload).execute()
                    st.toast("Cliente cadastrado!")

                # Reseta o estado da tela
                st.session_state.id_selecionado = None
                st.session_state.val_nome = ""
                st.session_state.val_email = ""
                st.session_state.val_estado = lista_estados[0] if lista_estados else ""
                st.rerun()
            else:
                st.error("Preencha Nome e Email!")

    with col_deletar:
        if st.session_state.id_selecionado:
            if st.button("❌ Deletar", type="secondary", use_container_width=True):
                # DELETE
                supabase.table("clientes").delete().eq("id", st.session_state.id_selecionado).execute()
                st.toast("Cliente removido!")

                st.session_state.id_selecionado = None
                st.session_state.val_nome = ""
                st.session_state.val_email = ""
                st.session_state.val_estado = lista_estados[0] if lista_estados else ""
                st.rerun()

    with col_limpar:
        if st.button("🧹 Limpar", use_container_width=True):
            st.session_state.id_selecionado = None
            st.session_state.val_nome = ""
            st.session_state.val_email = ""
            st.session_state.val_estado = lista_estados[0] if lista_estados else ""
            st.rerun()