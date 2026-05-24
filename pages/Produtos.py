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
    res = supabase.table("estados").select("sigla, nome").execute()
    return pd.DataFrame(res.data)


def buscar_clientes():
    res = supabase.table("clientes").select("id, nome, email, estado_sigla").execute()
    return pd.DataFrame(res.data)


# Carrega os dados das tabelas
df_estados = buscar_estados()
lista_estados = df_estados["sigla"].tolist() if not df_estados.empty else []

df_clientes = buscar_clientes()
lista_ids = ["--- Novo Registro ---"] + df_clientes["id"].tolist() if not df_clientes.empty else ["--- Novo Registro ---"]

# -----------------------------------------------------------------------------
# Layout do Aplicativo
# -----------------------------------------------------------------------------
col_form, col_tabela = st.columns([1, 2])

# -----------------------------------------------------------------------------
# Coluna da Esquerda: FORMULÁRIO (CREATE / UPDATE / DELETE)
# -----------------------------------------------------------------------------
with col_form:
    st.subheader("📝 Formulário do Cliente")

    # SELETOR DE REGISTRO: É este componente que define se criamos ou editamos.
    # Ele elimina o bug de cliques fantasmas no dataframe que travavam a tela.
    id_selecionado = st.selectbox("Selecione um ID para Editar/Deletar:", options=lista_ids)

    # Inicializa variáveis base do formulário
    dados_cliente = None
    nome_inicial = ""
    email_inicial = ""
    estado_inicial = lista_estados[0] if lista_estados else ""

    # Se um ID válido foi selecionado, busca os dados correspondentes no DataFrame carregado
    if id_selecionado != "--- Novo Registro ---":
        dados_cliente = df_clientes[df_clientes["id"] == id_selecionado].iloc[0]
        nome_inicial = str(dados_cliente["nome"])
        email_inicial = str(dados_cliente["email"])
        estado_inicial = str(dados_cliente["estado_sigla"])
        st.info(f"Modo: Editando ID {id_selecionado}")
    else:
        st.success("Modo: Criando Novo Registro")

    # Inputs de texto - O uso do 'key' atrelado ao ID reseta o campo se o usuário mudar de ID
    chave_id = "novo" if id_selecionado == "--- Novo Registro ---" else str(id_selecionado)

    nome_input = st.text_input("Nome", value=nome_inicial, key=f"nome_{chave_id}")
    email_input = st.text_input("Email", value=email_inicial, key=f"email_{chave_id}")

    # Localiza o índice do estado no selectbox de forma segura
    try:
        idx_estado = lista_estados.index(estado_inicial)
    except ValueError:
        idx_estado = 0

    estado_input = st.selectbox("Estado", options=lista_estados, index=idx_estado, key=f"estado_{chave_id}")

    # Botões de Operação do CRUD
    st.write("")
    col_salvar, col_deletar = st.columns(2)

    with col_salvar:
        if st.button("💾 Salvar Registro", type="primary", use_container_width=True):
            if nome_input.strip() and email_input.strip():
                payload = {
                    "nome": nome_input,
                    "email": email_input,
                    "estado_sigla": estado_input
                }

                if id_selecionado != "--- Novo Registro ---":
                    # UPDATE
                    supabase.table("clientes").update(payload).eq("id", id_selecionado).execute()
                    st.toast("Cliente atualizado com sucesso!")
                else:
                    # CREATE
                    supabase.table("clientes").insert(payload).execute()
                    st.toast("Cliente cadastrado com sucesso!")

                st.rerun()
            else:
                st.error("Preencha todos os campos obrigatórios.")

    with col_deletar:
        if id_selecionado != "--- Novo Registro ---":
            if st.button("❌ Deletar", type="secondary", use_container_width=True):
                # DELETE
                supabase.table("clientes").delete().eq("id", id_selecionado).execute()
                st.toast("Cliente removido do banco de dados!")
                st.rerun()

# -----------------------------------------------------------------------------
# Coluna da Direita: DATAFRAME (READ)
# -----------------------------------------------------------------------------
with col_tabela:
    st.subheader("📊 Clientes Cadastrados")
    st.caption("Para editar ou excluir um registro, selecione o ID correspondente no menu lateral.")

    if not df_clientes.empty:
        # Exibe o DataFrame de forma estática, apenas para leitura.
        # Isso impede que cliques acidentais quebrem ou travem a interface.
        st.dataframe(
            df_clientes,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum cliente cadastrado no banco de dados.")