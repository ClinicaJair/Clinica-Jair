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


# Carrega os estados para o selectbox
df_estados = buscar_estados()
lista_estados = df_estados["sigla"].tolist() if not df_estados.empty else []

# -----------------------------------------------------------------------------
# Inicialização do Estado da Tela (Session State)
# -----------------------------------------------------------------------------
if "cliente_selecionado" not in st.session_state:
    st.session_state.cliente_selecionado = {"id": None, "nome": "", "email": "", "estado_sigla": lista_estados[0] if lista_estados else ""}

# -----------------------------------------------------------------------------
# Interface Principal: Divide a tela em duas colunas (Formulário e Tabela)
# -----------------------------------------------------------------------------
col_form, col_tabela = st.columns([1, 2])

with col_form:
    st.subheader("📝 Formulário do Cliente")

    # Campos do formulário linkados ao session_state
    id_atual = st.session_state.cliente_selecionado["id"]

    # Mostra se estamos editando ou criando um novo
    if id_atual:
        st.info(f"Editando Cliente ID: {id_atual}")
    else:
        st.success("Criando Novo Cliente")

    # Inputs de texto
    nome = st.text_input("Nome", value=st.session_state.cliente_selecionado["nome"])
    email = st.text_input("Email", value=st.session_state.cliente_selecionado["email"])

    # Selectbox buscando dados da tabela estrangeira
    idx_estado = lista_estados.index(st.session_state.cliente_selecionado["estado_sigla"]) if st.session_state.cliente_selecionado[
                                                                                                  "estado_sigla"] in lista_estados else 0
    estado = st.selectbox("Estado", options=lista_estados, index=idx_estado)

    # Botões de Ação (C, U, D)
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("Salvar / Gravar", type="primary", use_container_width=True):
            if nome and email:
                dados = {"nome": nome, "email": email, "estado_sigla": estado}
                if id_atual:
                    # UPDATE
                    supabase.table("clientes").update(dados).eq("id", id_atual).execute()
                    st.toast("Cliente atualizado com sucesso!")
                else:
                    # CREATE
                    supabase.table("clientes").insert(dados).execute()
                    st.toast("Cliente cadastrado com sucesso!")

                # Reseta o formulário e recarrega a página
                st.session_state.cliente_selecionado = {"id": None, "nome": "", "email": "", "estado_sigla": lista_estados[0]}
                st.rerun()
            else:
                st.error("Preencha Nome e Email!")

    with col_btn2:
        # Só habilita o botão deletar se houver um registro selecionado
        if id_atual:
            if st.button("❌ Deletar", type="secondary", use_container_width=True):
                # DELETE
                supabase.table("clientes").delete().eq("id", id_atual).execute()
                st.toast("Cliente removido!")
                st.session_state.cliente_selecionado = {"id": None, "nome": "", "email": "", "estado_sigla": lista_estados[0]}
                st.rerun()

    with col_btn3:
        if st.button("Limpar", use_container_width=True):
            st.session_state.cliente_selecionado = {"id": None, "nome": "", "email": "", "estado_sigla": lista_estados[0]}
            st.rerun()

with col_tabela:
    st.subheader("📊 Clientes Cadastrados (READ)")
    st.write("Clique na linha para carregar os dados no formulário lateral:")

    # Busca os dados atuais do banco
    df_clientes = buscar_clientes()

    if not df_clientes.empty:
        # Configura a seleção de linhas nativa do st.dataframe
        evento_selecao = st.dataframe(
            df_clientes,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",  # Faz a tela recarregar ao clicar
            selection_mode="single-row"  # Permite selecionar uma linha por vez
        )

        # Monitora se o usuário clicou em alguma linha
        if evento_selecao and "rows" in evento_selecao["selection"] and len(evento_selecao["selection"]["rows"]) > 0:
            idx_linha_clicada = evento_selecao["selection"]["rows"][0]
            dados_cliente = df_clientes.iloc[idx_linha_clicada]

            # Se o cliente clicado for diferente do que já está na memória, atualiza o formulário
            if st.session_state.cliente_selecionado["id"] != int(dados_cliente["id"]):
                st.session_state.cliente_selecionado = {
                    "id": int(dados_cliente["id"]),
                    "nome": str(dados_cliente["nome"]),
                    "email": str(dados_cliente["email"]),
                    "estado_sigla": str(dados_cliente["estado_sigla"])
                }
                st.rerun()
    else:
        st.info("Nenhum cliente cadastrado ainda.")