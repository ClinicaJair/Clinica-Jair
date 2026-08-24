import io
import time
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import streamlit as st
from fpdf import FPDF
from supabase import Client, create_client

# ==========================================
# 1. Configuração da Página
# ==========================================
st.set_page_config(page_title="Cadastro de Especialidades Médicas", layout="wide")

# CSS para customizar a mensagem centralizada na tela
st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    header { visibility: hidden; height: 0px; }

    /* Estilização do Toast / Popup Centralizado */
    .mensagem-centralizada {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 99999;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        text-align: center;
        animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translate(-50%, -10px); }
        to { opacity: 1; transform: translate(-50%, 0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 2. Conexão com o Supabase
# ==========================================
@st.cache_resource
def iniciar_conexao():
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erro ao carregar credenciais do Supabase: {e}")
        st.stop()


supabase = iniciar_conexao()


# ==========================================
# 3. Função para Gerar Relatório PDF
# ==========================================
def gerar_relatorio_pdf(df):
    """Gera um PDF formatado convertendo strings para evitar erros de caractere."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("helvetica", size=10)

    def limpar_texto(txt):
        if not txt:
            return ""
        return str(txt).encode("latin-1", "ignore").decode("latin-1")

    # --- CABEÇALHO DO RELATÓRIO ---
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 8, limpar_texto("ESPECIALIDADES MÉDICAS"), align="C")
    pdf.ln(8)

    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        0,
        6,
        limpar_texto("Relatório Geral de Especialidades Médicas Cadastradas"),
        align="C",
    )
    pdf.ln(6)

    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, 26, 200, 26)
    pdf.ln(8)

    # --- CABEÇALHO DA TABELA ---
    largura_codigo = 30
    largura_nome = 160

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(largura_codigo, 8, limpar_texto(" Código"), border=1, fill=True)
    pdf.cell(largura_nome, 8, limpar_texto(" Nome da Especialidade"), border=1, fill=True)
    pdf.ln(8)

    # --- DADOS DA TABELA ---
    pdf.set_font("helvetica", "", 9)

    for _, row in df.iterrows():
        cod = limpar_texto(row.get("codigo", "")) if pd.notna(row.get("codigo")) else ""
        nome = limpar_texto(row.get("nome", "")) if pd.notna(row.get("nome")) else ""

        if len(nome) > 80:
            nome = nome[:77] + "..."

        pdf.cell(largura_codigo, 7, f" {cod}", border=1)
        pdf.cell(largura_nome, 7, f" {nome}", border=1)
        pdf.ln(7)

    return bytes(pdf.output())


# ==========================================
# 4. Inicialização do Session State e Funções
# ==========================================
if "especialidade_selecionada" not in st.session_state:
    st.session_state.especialidade_selecionada = None
if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
if "table_key" not in st.session_state:
    st.session_state.table_key = 0


def limpar_campos_e_selecao():
    """Reseta o registro selecionado e força novas chaves para o formulário e a tabela."""
    st.session_state.especialidade_selecionada = None
    st.session_state.update_trigger += 1
    st.session_state.table_key += 1


def carregar_dados(pesquisa=""):
    try:
        if pesquisa:
            response = (
                supabase.table("especialidades")
                .select("*")
                .ilike("nome", f"%{pesquisa}%")
                .execute()
            )
        else:
            response = supabase.table("especialidades").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def obter_proximo_codigo():
    """Busca o maior código numérico cadastrado no Supabase e retorna o próximo valor."""
    try:
        res = (
            supabase.table("especialidades")
            .select("codigo")
            .order("codigo", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            ultimo_codigo = res.data[0]["codigo"]
            try:
                return str(int(ultimo_codigo) + 1)
            except ValueError:
                return "1"
        return "1"
    except Exception:
        return "1"


# Modal de Confirmação para Deletar
@st.dialog("⚠️ Confirmar Exclusão")
def dialog_confirmar_deletar(codigo_deletar):
    st.write(f"Deseja realmente deletar o registro **Código {codigo_deletar}**?")
    col_sim, col_nao = st.columns(2)

    with col_sim:
        if st.button("Sim", use_container_width=True, type="primary"):
            try:
                supabase.table("especialidades").delete().eq("codigo", codigo_deletar).execute()
                limpar_campos_e_selecao()
                st.session_state["mensagem_sucesso"] = "Registro removido com sucesso!"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao deletar registro: {e}")

    with col_nao:
        if st.button("Não", use_container_width=True):
            st.rerun()


# ==========================================
# EXIBIÇÃO DA MENSAGEM TEMPORÁRIA CENTRALIZADA
# ==========================================
if "mensagem_sucesso" in st.session_state:
    mensagem = st.session_state.pop("mensagem_sucesso")
    container_msg = st.empty()

    # Renderiza a mensagem estilo popup no topo/centro
    container_msg.markdown(
        f'<div class="mensagem-centralizada">✅ {mensagem}</div>',
        unsafe_allow_html=True
    )

    # Aguarda 3 segundos e remove do DOM
    time.sleep(3)
    container_msg.empty()

especialidade_sel = st.session_state.especialidade_selecionada
id_ativo = especialidade_sel.get("codigo") if especialidade_sel else None

st.subheader("🏥 Cadastro de Especialidades Médicas")

# ==========================================
# 5. Formulário de Cadastro e Edição
# ==========================================
if id_ativo:
    st.markdown(f"##### ✏️ Editando Especialidade: Código {id_ativo}")
    codigo_exibicao = str(id_ativo)
else:
    st.markdown("##### ➕ Nova Especialidade")
    codigo_exibicao = obter_proximo_codigo()

with st.form(key=f"form_cliente_{st.session_state.update_trigger}"):
    # Linha 1: Dados Principais
    col1, col2 = st.columns([1, 4])
    with col1:
        codigo = st.text_input(
            "Código", value=codigo_exibicao, disabled=True, help="Gerado automaticamente"
        )
    with col2:
        nome = st.text_input(
            "Especialidade", value=especialidade_sel.get("nome", "") if especialidade_sel else ""
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Botões de ação do formulário
    col15, col16, col17, col18 = st.columns(4)
    submit_criar = col15.form_submit_button(
        "➕ Inserir", use_container_width=True
    )
    submit_atualizar = col16.form_submit_button(
        "✏️ Atualizar", use_container_width=True
    )
    submit_deletar = col17.form_submit_button(
        "🗑️ Deletar", use_container_width=True
    )
    submit_limpar = col18.form_submit_button(
        "🧹 Limpar", use_container_width=True
    )

# ==========================================
# 6. Lógica de Persistência (CRUD)
# ==========================================
payload = {
    "codigo": codigo,
    "nome": nome,
}

# --- INSERIR ---
if submit_criar:
    if nome:
        try:
            supabase.table("especialidades").insert(payload).execute()
            st.session_state["mensagem_sucesso"] = f"Especialidade cadastrada com sucesso sob o Código {codigo}!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir dados no banco: {e}")
    else:
        st.warning("Preencha obrigatoriamente o campo 'Nome'.")

# --- ATUALIZAR ---
if submit_atualizar:
    if id_ativo:
        try:
            supabase.table("especialidades").update(payload).eq("codigo", id_ativo).execute()
            st.session_state["mensagem_sucesso"] = "Registro atualizado com sucesso!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar registro: {e}")
    else:
        st.warning("Selecione um registro na tabela antes de tentar atualizar.")

# --- DELETAR ---
if submit_deletar:
    if id_ativo:
        dialog_confirmar_deletar(id_ativo)
    else:
        st.warning("Selecione um registro na tabela antes de tentar deletar.")

# --- LIMPAR ---
if submit_limpar:
    limpar_campos_e_selecao()
    st.rerun()

# ==========================================
# 7. Pesquisa, Tabela e Download em PDF (Fora do Form)
# ==========================================
st.markdown("---")
st.markdown("##### 🔍 Localizar Especialidades Médicas")

filtro = st.text_input(
    "Filtrar por Especialidade:", placeholder="Digite para buscar..."
)
df_dados = carregar_dados(filtro)

if not df_dados.empty:
    colunas_exibicao = [
        c for c in ["codigo", "nome"] if c in df_dados.columns
    ]

    evento_selecao = st.dataframe(
        df_dados[colunas_exibicao],
        selection_mode="single-row",
        on_select="rerun",
        use_container_width=True,
        key=f"tabela_especialidades_{st.session_state.table_key}",
        height=300,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão de download do relatório PDF
    try:
        pdf_data = gerar_relatorio_pdf(df_dados)
        st.download_button(
            label="📄 Gerar Relatório PDF",
            data=pdf_data,
            file_name="relatorio_especialidades.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Erro ao preparar arquivo PDF: {e}")

    # Processamento da seleção de linha na tabela
    linhas_selecionadas = evento_selecao.selection.get("rows", [])
    if linhas_selecionadas:
        indice_selecionado = linhas_selecionadas[0]
        dados_linha = df_dados.iloc[indice_selecionado].to_dict()

        if st.session_state.especialidade_selecionada != dados_linha:
            st.session_state.especialidade_selecionada = dados_linha
            st.rerun()
else:
    st.info("Nenhuma especialidade médica cadastrada ou encontrada.")