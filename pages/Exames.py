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
st.set_page_config(page_title="Cadastro de Exames", layout="wide")

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


def obter_dados_clinica():
    """Busca o primeiro registro da tabela clinicas para o cabeçalho."""
    try:
        res = supabase.table("clinicas").select("*").limit(1).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return {}
    except Exception:
        return {}


# ==========================================
# 3. Função para Gerar Relatório PDF
# ==========================================
def gerar_relatorio_pdf(df, dados_clinica):
    """Gera um PDF formatado com os dados da clínica no cabeçalho."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    def limpar_texto(txt):
        if not txt:
            return ""
        return str(txt).encode("latin-1", "ignore").decode("latin-1")

    # --- CABEÇALHO COM DADOS DA CLÍNICA ---
    fantasia = limpar_texto(dados_clinica.get("fantasia", "CLÍNICA MÉDICA"))
    endereco = limpar_texto(dados_clinica.get("endereco", ""))
    bairro = limpar_texto(dados_clinica.get("bairro", ""))
    cidade = limpar_texto(dados_clinica.get("cidade", ""))
    estado = limpar_texto(dados_clinica.get("estado", ""))
    cep = limpar_texto(dados_clinica.get("cep", ""))
    tel = limpar_texto(dados_clinica.get("telefone", ""))
    tel1 = limpar_texto(dados_clinica.get("telefone1", ""))
    email = limpar_texto(dados_clinica.get("email", ""))
    instagram = limpar_texto(dados_clinica.get("instagram", ""))

    # Nome da Clínica
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 6, fantasia, align="C")
    pdf.ln(6)

    # Endereço Montado
    pdf.set_font("helvetica", "", 9)
    partes_end = []
    if endereco:
        partes_end.append(endereco)
    if bairro:
        partes_end.append(f"Bairro: {bairro}")
    if cidade or estado:
        partes_end.append(f"{cidade}/{estado}".strip("/"))
    if cep:
        partes_end.append(f"CEP: {cep}")

    texto_endereco = " - ".join(partes_end)
    if texto_endereco:
        pdf.cell(0, 5, texto_endereco, align="C")
        pdf.ln(5)

    # Telefones, E-mail, Instagram
    partes_contato = []
    telefones = "/".join(filter(None, [tel, tel1]))
    if telefones:
        partes_contato.append(f"Tel: {telefones}")
    if email:
        partes_contato.append(f"E-mail: {email}")
    if instagram:
        partes_contato.append(f"Instagram: {instagram}")

    texto_contato = " | ".join(partes_contato)
    if texto_contato:
        pdf.cell(0, 5, texto_contato, align="C")
        pdf.ln(5)

    # Linha Divisória
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(6)

    # Título do Relatório
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 6, limpar_texto("RELATÓRIO DE EXAMES CADASTRADOS"), align="C")
    pdf.ln(8)

    # --- CABEÇALHO DA TABELA ---
    largura_codigo = 30
    largura_nome = 120
    largura_valor = 40

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(largura_codigo, 8, limpar_texto(" Código"), border=1, fill=True)
    pdf.cell(largura_nome, 8, limpar_texto(" Nome do Exame"), border=1, fill=True)
    pdf.cell(largura_valor, 8, limpar_texto(" Valor do Exame (R$)"), border=1, fill=True)
    pdf.ln(8)

    # --- DADOS DA TABELA ---
    pdf.set_font("helvetica", "", 9)

    for _, row in df.iterrows():
        cod = limpar_texto(row.get("codigo", "")) if pd.notna(row.get("codigo")) else ""
        nome = limpar_texto(row.get("nome", "")) if pd.notna(row.get("nome")) else ""

        val_raw = row.get("valor", 0.0)
        try:
            valor_fmt = f"{float(val_raw):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            valor_fmt = "0,00"

        if len(nome) > 55:
            nome = nome[:52] + "..."

        pdf.cell(largura_codigo, 7, f" {cod}", border=1)
        pdf.cell(largura_nome, 7, f" {nome}", border=1)
        pdf.cell(largura_valor, 7, f" R$ {valor_fmt}", border=1)
        pdf.ln(7)

    return bytes(pdf.output())


# ==========================================
# 4. Inicialização do Session State e Funções
# ==========================================
if "exame_selecionado" not in st.session_state:
    st.session_state.exame_selecionado = None
if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
if "table_key" not in st.session_state:
    st.session_state.table_key = 0


def limpar_campos_e_selecao():
    """Reseta o registro selecionado e força novas chaves para o formulário e a tabela."""
    st.session_state.exame_selecionado = None
    st.session_state.update_trigger += 1
    st.session_state.table_key += 1


def carregar_dados(pesquisa=""):
    try:
        if pesquisa:
            response = (
                supabase.table("exames")
                .select("*")
                .ilike("nome", f"%{pesquisa}%")
                .execute()
            )
        else:
            response = supabase.table("exames").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def obter_proximo_codigo():
    """Busca o maior código numérico cadastrado no Supabase e retorna o próximo valor."""
    try:
        res = (
            supabase.table("exames")
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
                supabase.table("exames").delete().eq("codigo", codigo_deletar).execute()
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

exame_sel = st.session_state.exame_selecionado
id_ativo = exame_sel.get("codigo") if exame_sel else None

st.subheader("🧪 Cadastro de Exames")

# ==========================================
# 5. Formulário de Cadastro e Edição
# ==========================================
if id_ativo:
    st.markdown(f"##### ✏️ Editando Exame: Código {id_ativo}")
    codigo_exibicao = str(id_ativo)
else:
    st.markdown("##### ➕ Novo Exame")
    codigo_exibicao = obter_proximo_codigo()

with st.form(key=f"form_exame_{st.session_state.update_trigger}"):
    # Linha 1: Dados Principais e Valor
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        codigo = st.text_input(
            "Código", value=codigo_exibicao, disabled=True, help="Gerado automaticamente"
        )
    with col2:
        nome = st.text_input(
            "Nome do Exame", value=exame_sel.get("nome", "") if exame_sel else ""
        )
    with col3:
        valor_padrao = float(exame_sel.get("valor", 0.0)) if exame_sel and exame_sel.get(
            "valor") is not None else 0.0
        valor = st.number_input(
            "Valor do Exame (R$)", value=valor_padrao, min_value=0.0, step=10.0, format="%.2f"
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
    "valor": valor,
}

# --- INSERIR ---
if submit_criar:
    if nome:
        try:
            supabase.table("exames").insert(payload).execute()
            st.session_state["mensagem_sucesso"] = f"Exame cadastrado com sucesso sob o Código {codigo}!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir dados no banco: {e}")
    else:
        st.warning("Preencha obrigatoriamente o campo 'Nome do Exame'.")

# --- ATUALIZAR ---
if submit_atualizar:
    if id_ativo:
        try:
            supabase.table("exames").update(payload).eq("codigo", id_ativo).execute()
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
st.markdown("##### 🔍 Localizar Exames")

filtro = st.text_input(
    "Filtrar por Exame:", placeholder="Digite para buscar..."
)
df_dados = carregar_dados(filtro)

if not df_dados.empty:
    colunas_exibicao = [
        c for c in ["codigo", "nome", "valor"] if c in df_dados.columns
    ]

    # Exibição configurada com a coluna de Valor formatada em R$
    evento_selecao = st.dataframe(
        df_dados[colunas_exibicao],
        column_config={
            "codigo": st.column_config.TextColumn("Código"),
            "nome": st.column_config.TextColumn("Nome do Exame"),
            "valor": st.column_config.NumberColumn(
                "Valor do Exame",
                format="R$ %.2f"
            ),
        },
        selection_mode="single-row",
        on_select="rerun",
        use_container_width=True,
        key=f"tabela_exames_{st.session_state.table_key}",
        height=300,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão de download do relatório PDF
    try:
        dados_clinica = obter_dados_clinica()
        pdf_data = gerar_relatorio_pdf(df_dados, dados_clinica)
        st.download_button(
            label="📄 Gerar Relatório PDF",
            data=pdf_data,
            file_name="relatorio_exames.pdf",
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

        if st.session_state.exame_selecionado != dados_linha:
            st.session_state.exame_selecionado = dados_linha
            st.rerun()
else:
    st.info("Nenhum exame cadastrado ou encontrado.")