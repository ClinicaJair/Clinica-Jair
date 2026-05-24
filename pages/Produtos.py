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


# Carrega os estados do banco
df_estados = buscar_estados()
lista_estados = df_estados["sigla"].tolist() if not df_estados.empty else []

# -----------------------------------------------------------------------------
# Inicialização das variáveis de controle (Session State)
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
# Lógica de Captura do Clique no DataFrame (Processado ANTES de desenhar a tela)
# -----------------------------------------------------------------------------
df_clientes = buscar_clientes()

# Criamos uma coluna visível de seleção para facilitar o clique do usuário
if not df_clientes.empty:
    # Captura se o usuário selecionou uma linha na tabela lateral
    col1, col2 = st.columns([1, 2])
else:
    col1, col2 = st.columns([1, 2])

# -----------------------------------------------------------------------------
# Coluna da Direita: Exibição da Tabela (READ) primeiro para capturar o clique
# -----------------------------------------------------------------------------
with col2:
    st.subheader("📊 Clientes Cadastrados")
    st.caption("Marque a caixa de seleção na linha desejada para carregar os dados no formulário:")

    if not df_clientes.empty:
        # st.dataframe configurado com seleção de linhas ativa
        tabela_interativa = st.dataframe(
            df_clientes,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Verifica se alguma linha foi marcada
        selecionados = tabela_interativa.get("selection", {}).get("rows", [])
        if selecionados:
            idx_linha = selecionados[0]
            linha_dados = df_clientes.iloc[idx_linha]

            # Atualiza o estado se for um ID diferente do atual na memória
            if st.session_state.id_selecionado != int(linha_dados["id"]):
                st.session_state.id_selecionado = int(linha_dados["id"])
                st.session_state.val_nome = str(linha_dados["nome"])
                st.session_state.val_email = str(linha_dados["email"])
                st.session_state.val_estado = str(linha_dados["estado_sigla"])
                st.rerun()
    else:
        st.info("Nenhum cliente cadastrado no banco de dados.")

# -----------------------------------------------------------------------------
# Coluna da Esquerda: Formulário Protegido (CREATE / UPDATE / DELETE)
# -----------------------------------------------------------------------------
with col1:
    st.subheader("📝 Formulário do Cliente")

    if st.session_state.id_selecionado:
        st.info(f"Modo: Editando ID {st.session_state.id_selecionado}")
    else:
        st.success("Modo: Criando Novo Registro")

    # Isolamos os inputs em um st.form. Isso destrava os campos completamente!
    with st.form("form_cliente", clear_on_submit=False):
        nome = st.text_input("Nome", value=st.session_state.val_nome)
        email = st.text_input("Email", value=st.session_state.val_email)

        # Define o índice correto do selectbox baseado no estado atual da memória
        try:
            idx_estado = lista_estados.index(st.session_state.val_estado)
        except ValueError:
            idx_estado = 0

        estado = st.selectbox("Estado", options=lista_estados, index=idx_estado)

        # Botão principal de envio dentro do formulário
        btn_salvar = st.form_submit_button("💾 Gravar / Salvar Dados", type="primary", use_container_width=True)

    # Lógica de salvar executada após o envio do form
    if btn_salvar:
        if nome.strip() and email.strip():
            dados_enviar = {"nome": nome, "email": email, "estado_sigla": estado}

            if st.session_state.id_selecionado:
                # UPDATE
                supabase.table("clientes").update(dados_enviar).eq("id", st.session_state.id_selecionado).execute()
                st.toast("Registro atualizado com sucesso!")
            else:
                # CREATE
                supabase.table("clientes").insert(dados_enviar).execute()
                st.toast("Registro criado com sucesso!")

            # Limpa o formulário e recarrega
            st.session_state.id_selecionado = None
            st.session_state.val_nome = ""
            st.session_state.val_email = ""
            st.session_state.val_estado = lista_estados[0] if lista_estados else ""
            st.rerun()
        else:
            st.error("Por favor, preencha o Nome e o Email do cliente.")

    # Botões de Deletar e Limpar ficam fora do formulário por questões de layout e funcionamento
    st.write("")
    col_d, col_l = st.columns(2)

    with col_d:
        if st.session_state.id_selecionado:
            if st.button("❌ Deletar Registro", type="secondary", use_container_width=True):
                # DELETE
                supabase.table("clientes").delete().eq("id", st.session_state.id_selecionado).execute()
                st.toast("Registro deletado com sucesso!")

                st.session_state.id_selecionado = None
                st.session_state.val_nome = ""
                st.session_state.val_email = ""
                st.session_state.val_estado = lista_estados[0] if lista_estados else ""
                st.rerun()

    with col_l:
        if st.button("🧹 Limpar / Novo", use_container_width=True):
            st.session_state.id_selecionado = None
            st.session_state.val_nome = ""
            st.session_state.val_email = ""
            st.session_state.val_estado = lista_estados[0] if lista_estados else ""
            st.rerun()