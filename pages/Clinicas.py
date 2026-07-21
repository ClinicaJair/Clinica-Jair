import io
import time
import pandas as pd
import streamlit as st
from fpdf import FPDF
from supabase import Client, create_client

# ==========================================
# 1. Configuração da Página
# ==========================================
st.set_page_config(page_title="Cadastro de Clínicas", layout="wide")

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
    pdf.cell(0, 8, limpar_texto("SISTEMA DE GESTÃO DE CLÍNICAS"), ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        0,
        6,
        limpar_texto("Relatório Geral de Clínicas Cadastradas"),
        ln=True,
        align="C",
    )

    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, 26, 200, 26)
    pdf.ln(8)

    # --- CABEÇALHO DA TABELA ---
    largura_fantasia = 90
    largura_cnpj = 50
    largura_telefone = 50

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(largura_fantasia, 8, limpar_texto(" Nome Fantasia"), border=1, fill=True)
    pdf.cell(largura_cnpj, 8, limpar_texto(" CNPJ"), border=1, fill=True)
    pdf.cell(
        largura_telefone,
        8,
        limpar_texto(" Telefone"),
        border=1,
        ln=True,
        fill=True,
    )

    # --- DADOS DA TABELA ---
    pdf.set_font("helvetica", "", 9)

    for _, row in df.iterrows():
        fantasia = (
            limpar_texto(row.get("fantasia", ""))
            if pd.notna(row.get("fantasia"))
            else ""
        )
        cnpj = (
            limpar_texto(row.get("cnpj", "")) if pd.notna(row.get("cnpj")) else ""
        )
        telefone = (
            limpar_texto(row.get("telefone", ""))
            if pd.notna(row.get("telefone"))
            else ""
        )

        if len(fantasia) > 45:
            fantasia = fantasia[:42] + "..."

        pdf.cell(largura_fantasia, 7, f" {fantasia}", border=1)
        pdf.cell(largura_cnpj, 7, f" {cnpj}", border=1)
        pdf.cell(largura_telefone, 7, f" {telefone}", border=1, ln=True)

    return bytes(pdf.output())


# ==========================================
# 4. Inicialização do Session State e Funções
# ==========================================
if "clinica_selecionada" not in st.session_state:
    st.session_state.clinica_selecionada = None
if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
if "table_key" not in st.session_state:
    st.session_state.table_key = 0


def limpar_campos_e_selecao():
    """Reseta a clínica selecionada e força novas chaves para o formulário e a tabela."""
    st.session_state.clinica_selecionada = None
    st.session_state.update_trigger += 1
    st.session_state.table_key += 1


def carregar_dados(pesquisa=""):
    try:
        if pesquisa:
            response = (
                supabase.table("clinicas")
                .select("*")
                .ilike("razao", f"%{pesquisa}%")
                .execute()
            )
        else:
            response = supabase.table("clinicas").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def obter_proximo_codigo():
    """Busca o maior código numérico cadastrado no Supabase e retorna o próximo valor."""
    try:
        res = (
            supabase.table("clinicas")
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
                supabase.table("clinicas").delete().eq("codigo", codigo_deletar).execute()
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

clinica_sel = st.session_state.clinica_selecionada
id_ativo = clinica_sel.get("codigo") if clinica_sel else None

st.subheader("🏥 Cadastro de Clínicas")

# ==========================================
# 5. Interface Gráfica em Duas Colunas
# ==========================================
col_esquerda, col_direita = st.columns([1.7, 1.3])

# ------------------------------------------
# COLUNA ESQUERDA: Formulário de Cadastro e Edição
# ------------------------------------------
with col_esquerda:
    if id_ativo:
        st.markdown(f"##### ✏️ Editando Clínica: Código {id_ativo}")
        codigo_exibicao = str(id_ativo)
    else:
        st.markdown("##### ➕ Nova Clínica")
        codigo_exibicao = obter_proximo_codigo()

    with st.form(key=f"form_cliente_{st.session_state.update_trigger}"):

        # Linha 1: Dados Principais
        col1, col2, col3 = st.columns([1, 2.5, 2])
        with col1:
            codigo = st.text_input(
                "Código", value=codigo_exibicao, disabled=True, help="Gerado automaticamente"
            )
        with col2:
            razao = st.text_input(
                "Razão Social", value=clinica_sel["razao"] if clinica_sel else ""
            )
        with col3:
            fantasia = st.text_input(
                "Nome Fantasia", value=clinica_sel["fantasia"] if clinica_sel else ""
            )

        # Linha 2: Documentações e Fundação
        col4, col5, col6 = st.columns([2, 2, 1.5])
        with col4:
            cnpj = st.text_input(
                "CNPJ", value=clinica_sel["cnpj"] if clinica_sel else ""
            )
        with col5:
            inscricao = st.text_input(
                "Insc. Estadual", value=clinica_sel["inscricao"] if clinica_sel else ""
            )
        with col6:
            data_inicial = None
            if clinica_sel and clinica_sel.get("data_fundacao"):
                try:
                    data_inicial = pd.to_datetime(
                        clinica_sel["data_fundacao"], dayfirst=True
                    ).date()
                except Exception:
                    data_inicial = None

            data_fundacao_val = st.date_input(
                "Fundação", value=data_inicial, format="DD/MM/YYYY"
            )

        # Linha 3: Localização (Endereço)
        col7, col8, col9 = st.columns([1.5, 3.5, 1.2])
        with col7:
            cep = st.text_input(
                "CEP", value=clinica_sel["cep"] if clinica_sel else ""
            )
        with col8:
            endereco = st.text_input(
                "Endereço", value=clinica_sel["endereco"] if clinica_sel else ""
            )
        with col9:
            estado = st.text_input(
                "Estado", value=clinica_sel["estado"] if clinica_sel else ""
            )

        # Linha 4: Cidade e Bairro
        col10, col11 = st.columns([1, 1])
        with col10:
            bairro = st.text_input(
                "Bairro", value=clinica_sel["bairro"] if clinica_sel else ""
            )
        with col11:
            cidade = st.text_input(
                "Cidade", value=clinica_sel["cidade"] if clinica_sel else ""
            )

        # Linha 5: Contato
        col12, col13, col14 = st.columns([1.2, 1.2, 2.1])
        with col12:
            telefone = st.text_input(
                "Telefone", value=clinica_sel["telefone"] if clinica_sel else ""
            )
        with col13:
            telefone1 = st.text_input(
                "Telefone 2",
                value=(
                    clinica_sel["telefone1"]
                    if clinica_sel and "telefone1" in clinica_sel
                    else ""
                ),
            )
        with col14:
            email = st.text_input(
                "E-mail", value=clinica_sel["email"] if clinica_sel else ""
            )

        # Linha 6: Links / Redes Sociais
        col14_2, col14_3 = st.columns([1, 1])
        with col14_2:
            site = st.text_input(
                "Site", value=clinica_sel["site"] if clinica_sel else ""
            )
        with col14_3:
            instagram = st.text_input(
                "Instagram", value=clinica_sel["instagram"] if clinica_sel else ""
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

# ------------------------------------------
# COLUNA DIREITA: Pesquisa e Seleção
# ------------------------------------------
with col_direita:
    st.markdown("##### 🔍 Localizar Clínica")
    filtro = st.text_input(
        "Filtrar por Razão Social ou Código:", placeholder="Digite para buscar..."
    )
    df_dados = carregar_dados(filtro)

    if not df_dados.empty:
        colunas_exibicao = [
            c for c in ["codigo", "razao", "fantasia"] if c in df_dados.columns
        ]

        evento_selecao = st.dataframe(
            df_dados[colunas_exibicao],
            selection_mode="single-row",
            on_select="rerun",
            use_container_width=True,
            key=f"tabela_clinicas_{st.session_state.table_key}",
            height=420,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        try:
            pdf_data = gerar_relatorio_pdf(df_dados)
            st.download_button(
                label="📄 Gerar Relatório PDF",
                data=pdf_data,
                file_name="relatorio_clinicas.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Erro ao preparar arquivo PDF: {e}")

        linhas_selecionadas = evento_selecao.selection.get("rows", [])
        if linhas_selecionadas:
            indice_selecionado = linhas_selecionadas[0]
            dados_linha = df_dados.iloc[indice_selecionado].to_dict()

            if st.session_state.clinica_selecionada != dados_linha:
                st.session_state.clinica_selecionada = dados_linha
                st.rerun()
    else:
        st.info("Nenhuma clínica cadastrada ou encontrada.")

# ==========================================
# 6. Lógica de Persistência (CRUD) e Ações
# ==========================================
data_fundacao_str = (
    data_fundacao_val.strftime("%d/%m/%Y") if data_fundacao_val else None
)

payload = {
    "codigo": codigo,
    "razao": razao,
    "fantasia": fantasia,
    "endereco": endereco,
    "cep": cep,
    "bairro": bairro,
    "cidade": cidade,
    "estado": estado,
    "telefone": telefone,
    "telefone1": telefone1,
    "cnpj": cnpj,
    "inscricao": inscricao,
    "data_fundacao": data_fundacao_str,
    "email": email,
    "site": site,
    "instagram": instagram,
}

# --- INSERIR ---
if submit_criar:
    if razao:
        try:
            supabase.table("clinicas").insert(payload).execute()
            st.session_state["mensagem_sucesso"] = f"Clínica cadastrada com sucesso sob o Código {codigo}!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir dados no banco: {e}")
    else:
        st.warning("Preencha obrigatoriamente o campo 'Razão Social'.")

# --- ATUALIZAR ---
if submit_atualizar:
    if id_ativo:
        try:
            supabase.table("clinicas").update(payload).eq("codigo", id_ativo).execute()
            st.session_state["mensagem_sucesso"] = "Registro atualizado com sucesso!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar registro: {e}")
    else:
        st.warning("Selecione uma clínica na tabela antes de tentar atualizar.")

# --- DELETAR ---
if submit_deletar:
    if id_ativo:
        dialog_confirmar_deletar(id_ativo)
    else:
        st.warning("Selecione uma clínica na tabela antes de tentar deletar.")

# --- LIMPAR ---
if submit_limpar:
    limpar_campos_e_selecao()
    st.rerun()