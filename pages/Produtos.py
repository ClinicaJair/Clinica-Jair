import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração da página
st.set_page_config(page_title="CRUD Clientes - Supabase", layout="wide")
st.title("👥 Cadastro de Clientes (CRUD)")

# =====================================================================
# CONEXÃO COM O SUPABASE
# Em produção, configure estes valores no arquivo .streamlit/secrets.toml
# =====================================================================
#SUPABASE_URL = st.secrets.get("SUPABASE_URL", "SUA_SUPABASE_URL_AQUI")
#SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "SUA_SUPABASE_ANON_KEY_AQUI")
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase: Client = init_connection()


# =====================================================================
# FUNÇÕES DE BUSCA DE DADOS (READ)
# =====================================================================
def carregar_estados():
    response = supabase.table("estado").select("id, sigla, nome").execute()
    return pd.DataFrame(response.data)


def carregar_clientes():
    # Faz um join simples trazendo o nome do estado junto
    response = supabase.table("cliente").select("id, nome, email, id_estado, estado(sigla)").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        # Formata a coluna de estado para ficar mais visual no dataframe
        if 'estado' in df.columns:
            df['uf'] = df['estado'].apply(lambda x: x['sigla'] if isinstance(x, dict) else None)
            df = df.drop(columns=['estado'])
        return df
    return pd.DataFrame(columns=["id", "nome", "email", "id_estado", "uf"])


# Carrega os dados iniciais
df_estados = carregar_estados()
df_clientes = carregar_clientes()

# Mapeamento de estados para o selectbox
opcoes_estado = {f"{row['sigla']} - {row['nome']}": row['id'] for _, row in df_estados.iterrows()}

# =====================================================================
# GERENCIAMENTO DE ESTADO DA SELEÇÃO (Clique no DataFrame)
# =====================================================================
# Usamos o st.session_state para guardar qual cliente está selecionado para edição
if "cliente_selecionado" not in st.session_state:
    st.session_state.cliente_selecionado = None

# Layout em duas colunas: Esquerda (Formulário) | Direita (Tabela/Visualização)
col_form, col_tabela = st.columns([1, 1.5])

# =====================================================================
# COLUNA DA DIREITA: Visualização e Seleção (Read)
# =====================================================================
with col_tabela:
    st.subheader("Clientes Cadastrados")
    st.caption("Selecione uma linha na tabela para Editar ou Deletar os dados.")

    # Configuração do Data Editor para funcionar como seleção de linha única
    event = st.dataframe(
        df_clientes[["id", "nome", "email", "uf"]],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Verifica se o usuário clicou/selecionou alguma linha do DataFrame
    if event and event.get("selection") and event["selection"].get("rows"):
        index_selecionado = event["selection"]["rows"][0]
        st.session_state.cliente_selecionado = df_clientes.iloc[index_selecionado].to_dict()
    elif st.button("🔄 Limpar Seleção / Novo Cadastro"):
        st.session_state.cliente_selecionado = None
        st.rerun()

# =====================================================================
# COLUNA DA ESQUERDA: Formulário de Cadastro (Create / Update / Delete)
# =====================================================================
with col_form:
    st.subheader("Formulário de Cliente")

    # Define se estamos editando ou criando um novo registro
    cliente_atual = st.session_state.cliente_selecionado
    modo_edicao = cliente_atual is not None

    # Valores padrão baseados na seleção ou vazios se for um novo cadastro
    default_nome = cliente_atual["nome"] if modo_edicao else ""
    default_email = cliente_atual["email"] if modo_edicao else ""

    # Encontra o index correto do estado no selectbox caso esteja editando
    default_index_estado = 0
    if modo_edicao and cliente_atual["id_estado"]:
        for i, id_est in enumerate(opcoes_estado.values()):
            if id_est == cliente_atual["id_estado"]:
                default_index_estado = i
                break

    # Campos do formulário
    with st.form(key="form_cliente", clear_on_submit=False):
        input_nome = st.text_input("Nome Completo", value=default_nome)
        input_email = st.text_input("E-mail", value=default_email)

        input_estado_str = st.selectbox(
            "Estado (UF)",
            options=list(opcoes_estado.keys()),
            index=default_index_estado
        )
        id_estado_sel = opcoes_estado[input_estado_str]

        # Botões de ação dentro do formulário
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if modo_edicao:
                botao_salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
            else:
                botao_salvar = st.form_submit_button("➕ Cadastrar", use_container_width=True)

        with col_btn2:
            # Botão de deletar só aparece se um registro existente estiver selecionado
            botao_deletar = st.form_submit_button("❌ Excluir Cliente", use_container_width=True, type="secondary") if modo_edicao else False

    # =====================================================================
    # PROCESSAMENTO DAS AÇÕES (CUD)
    # =====================================================================
    if botao_salvar:
        if not input_nome:
            st.error("O campo Nome é obrigatório!")
        else:
            dados_cliente = {
                "nome": input_nome,
                "email": input_email,
                "id_estado": id_estado_sel
            }

            if modo_edicao:
                # UPDATE
                supabase.table("cliente").update(dados_cliente).eq("id", cliente_atual["id"]).execute()
                st.success(f"Cliente '{input_nome}' atualizado com sucesso!")
            else:
                # CREATE
                supabase.table("cliente").insert(dados_cliente).execute()
                st.success(f"Cliente '{input_nome}' cadastrado com sucesso!")

            st.session_state.cliente_selecionado = None
            st.rerun()

    if botao_deletar:
        # DELETE
        supabase.table("cliente").delete().eq("id", cliente_atual["id"]).execute()
        st.toast(f"Cliente removido com sucesso!", icon="🗑️")
        st.session_state.cliente_selecionado = None
        st.rerun()