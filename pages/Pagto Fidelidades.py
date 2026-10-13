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
st.set_page_config(page_title="Pagamentos de Fidelidade", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    header { visibility: hidden; height: 0px; }

    /* Estilização dos Botões CRUD (Formulário) e Download */
    div[data-testid="stFormSubmitButton"] > button,
    div.stButton > button, 
    div.stDownloadButton > button {
        background-color: #81D4FA !important;
        color: #000000 !important;
        border: none !important;
        font-weight: bold !important;
        transition: background-color 0.3s ease, transform 0.1s ease !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover,
    div.stButton > button:hover, 
    div.stDownloadButton > button:hover {
        background-color: #4FC3F7 !important;
        color: #000000 !important;
        border: none !important;
    }

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


def buscar_pacientes():
    """Busca a lista de pacientes cadastrados na tabela 'pacientes'."""
    try:
        res = supabase.table("pacientes").select("codigo, nome").order("nome").execute()
        return res.data if res.data else []
    except Exception:
        return []


def buscar_planos_fidelidade():
    """Busca os planos de fidelidade cadastrados na tabela 'planosfidelidades'."""
    try:
        res = supabase.table("planosfidelidades").select("codigo, nome").order("nome").execute()
        return res.data if res.data else []
    except Exception:
        return []


# ==========================================
# 3. Função para Gerar Relatório PDF
# ==========================================
def gerar_relatorio_pdf(df, dados_clinica):
    """Gera um PDF formatado com os dados da clínica no cabeçalho."""
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    def limpar_texto(txt):
        if not txt:
            return ""
        return str(txt).encode("latin-1", "ignore").decode("latin-1")

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

    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 6, fantasia, align="C")
    pdf.ln(6)

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

    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y() + 2, 287, pdf.get_y() + 2)
    pdf.ln(6)

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 6, limpar_texto("RELATÓRIO DE PAGAMENTOS FIDELIDADE"), align="C")
    pdf.ln(8)

    # --- CABEÇALHO DA TABELA ---
    l_cod = 14
    l_data = 22
    l_codpac = 18
    l_pac = 55
    l_codplano = 18
    l_plano = 45
    l_vplano = 28
    l_vclinica = 28
    l_vfidelidade = 28
    l_tipo = 21

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(l_cod, 8, limpar_texto(" Cód."), border=1, fill=True)
    pdf.cell(l_data, 8, limpar_texto(" Data"), border=1, fill=True)
    pdf.cell(l_codpac, 8, limpar_texto(" Cód.Pac"), border=1, fill=True)
    pdf.cell(l_pac, 8, limpar_texto(" Paciente"), border=1, fill=True)
    pdf.cell(l_codplano, 8, limpar_texto(" Cód.Plano"), border=1, fill=True)
    pdf.cell(l_plano, 8, limpar_texto(" Plano"), border=1, fill=True)
    pdf.cell(l_vplano, 8, limpar_texto(" Vlr Plano"), border=1, fill=True)
    pdf.cell(l_vclinica, 8, limpar_texto(" Vlr Clínica"), border=1, fill=True)
    pdf.cell(l_vfidelidade, 8, limpar_texto(" Vlr Fidel."), border=1, fill=True)
    pdf.cell(l_tipo, 8, limpar_texto(" Tipo Pagto"), border=1, fill=True)
    pdf.ln(8)

    # --- DADOS DA TABELA ---
    pdf.set_font("helvetica", "", 8)

    def fmt_moeda(val):
        try:
            return f"{float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return "0,00"

    for _, row in df.iterrows():
        cod = limpar_texto(row.get("codigo", ""))
        dt_val = row.get("data", "")
        dt_fmt = pd.to_datetime(dt_val).strftime("%d/%m/%Y") if pd.notna(dt_val) and dt_val else ""
        codpac = limpar_texto(row.get("codpaciente", ""))
        pac = limpar_texto(row.get("paciente", ""))
        codplano_val = limpar_texto(row.get("codplano", ""))
        plano_val = limpar_texto(row.get("plano", ""))
        vplano = fmt_moeda(row.get("vlrplano", 0))
        vclinica = fmt_moeda(row.get("vlrclinica", 0))
        vfidelidade = fmt_moeda(row.get("vlrfidelidade", 0))
        tipo = limpar_texto(row.get("tipopagto", ""))

        if len(pac) > 28:
            pac = pac[:25] + "..."
        if len(plano_val) > 22:
            plano_val = plano_val[:19] + "..."

        pdf.cell(l_cod, 7, f" {cod}", border=1)
        pdf.cell(l_data, 7, f" {dt_fmt}", border=1)
        pdf.cell(l_codpac, 7, f" {codpac}", border=1)
        pdf.cell(l_pac, 7, f" {pac}", border=1)
        pdf.cell(l_codplano, 7, f" {codplano_val}", border=1)
        pdf.cell(l_plano, 7, f" {plano_val}", border=1)
        pdf.cell(l_vplano, 7, f" R$ {vplano}", border=1)
        pdf.cell(l_vclinica, 7, f" R$ {vclinica}", border=1)
        pdf.cell(l_vfidelidade, 7, f" R$ {vfidelidade}", border=1)
        pdf.cell(l_tipo, 7, f" {tipo}", border=1)
        pdf.ln(7)

    return bytes(pdf.output())


# ==========================================
# 4. Inicialização do Session State e Funções
# ==========================================
if "pagto_selecionado" not in st.session_state:
    st.session_state.pagto_selecionado = None
if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
if "table_key" not in st.session_state:
    st.session_state.table_key = 0


def limpar_campos_e_selecao():
    st.session_state.pagto_selecionado = None
    st.session_state.update_trigger += 1
    st.session_state.table_key += 1


def carregar_dados(pesquisa=""):
    try:
        if pesquisa:
            response = (
                supabase.table("pagtofidelidade")
                .select("*")
                .ilike("paciente", f"%{pesquisa}%")
                .execute()
            )
        else:
            response = supabase.table("pagtofidelidade").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def obter_proximo_codigo():
    try:
        res = (
            supabase.table("pagtofidelidade")
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


@st.dialog("⚠️ Confirmar Exclusão")
def dialog_confirmar_deletar(codigo_deletar):
    st.write(f"Deseja realmente deletar o registro **Código {codigo_deletar}**?")
    col_sim, col_nao = st.columns(2)

    with col_sim:
        if st.button("Sim", use_container_width=True, type="primary"):
            try:
                supabase.table("pagtofidelidade").delete().eq("codigo", codigo_deletar).execute()
                limpar_campos_e_selecao()
                st.session_state["mensagem_sucesso"] = "Registro removido com sucesso!"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao deletar registro: {e}")

    with col_nao:
        if st.button("Não", use_container_width=True):
            st.rerun()


if "mensagem_sucesso" in st.session_state:
    mensagem = st.session_state.pop("mensagem_sucesso")
    container_msg = st.empty()

    container_msg.markdown(
        f'<div class="mensagem-centralizada">✅ {mensagem}</div>',
        unsafe_allow_html=True,
    )

    time.sleep(3)
    container_msg.empty()

pagto_sel = st.session_state.pagto_selecionado
id_ativo = pagto_sel.get("codigo") if pagto_sel else None

st.subheader("Pagamento de Fidelidade")

# ==========================================
# 5. Busca e Seleção do Paciente e Plano
# ==========================================
pacientes_lista = buscar_pacientes()
opcoes_pacientes = {f"{p['codigo']} - {p['nome']}": p for p in pacientes_lista}

index_paciente_atual = 0
if pagto_sel and pagto_sel.get("codpaciente"):
    for idx, (label, obj) in enumerate(opcoes_pacientes.items()):
        if str(obj["codigo"]) == str(pagto_sel.get("codpaciente")):
            index_paciente_atual = idx
            break

paciente_selecionado_label = st.selectbox(
    "🔍 Pesquisar/Selecionar Paciente (Tabela Pacientes):",
    options=list(opcoes_pacientes.keys()),
    index=index_paciente_atual if opcoes_pacientes else None,
    help="Selecione o paciente cadastrado na tabela 'pacientes' para vincular ao pagamento.",
    key=f"select_paciente_{st.session_state.update_trigger}"
)

paciente_obj = opcoes_pacientes.get(paciente_selecionado_label, {})
cod_paciente_val = str(paciente_obj.get("codigo", "")) if paciente_obj else ""
nome_paciente_val = paciente_obj.get("nome", "") if paciente_obj else ""

# Carrega Planos de Fidelidade
planos_lista = buscar_planos_fidelidade()
opcoes_planos = {f"{p['codigo']} - {p['nome']}": p for p in planos_lista}

index_plano_atual = 0
if pagto_sel and pagto_sel.get("codplano"):
    for idx, (label, obj) in enumerate(opcoes_planos.items()):
        if str(obj["codigo"]) == str(pagto_sel.get("codplano")):
            index_plano_atual = idx
            break

plano_selecionado_label = st.selectbox(
    "🎁 Pesquisar/Selecionar Plano de Fidelidade:",
    options=list(opcoes_planos.keys()),
    index=index_plano_atual if opcoes_planos else None,
    help="Selecione o plano de fidelidade para vincular ao pagamento.",
    key=f"select_plano_{st.session_state.update_trigger}"
)

plano_obj = opcoes_planos.get(plano_selecionado_label, {})
cod_plano_val = str(plano_obj.get("codigo", "")) if plano_obj else ""
nome_plano_val = plano_obj.get("nome", "") if plano_obj else ""

# ==========================================
# 6. Formulário de Cadastro e Edição
# ==========================================
if id_ativo:
    st.markdown(f"##### ✏️ Editando Pagamento Fidelidade: Código {id_ativo}")
    codigo_exibicao = str(id_ativo)
else:
    st.markdown("##### ➕ Novo Pagamento Fidelidade")
    codigo_exibicao = obter_proximo_codigo()

with st.form(key=f"form_pagtofidelidade_{st.session_state.update_trigger}"):
    # Linha 1: Código, Data, Cód. Paciente, Nome Paciente
    col1, col2, col3, col4 = st.columns([1, 1.2, 1.2, 3])
    with col1:
        codigo = st.text_input(
            "Código",
            value=codigo_exibicao,
            disabled=True,
            help="Gerado automaticamente",
        )
    with col2:
        dt_padrao = (
            datetime.datetime.strptime(pagto_sel.get("data"), "%Y-%m-%d").date()
            if pagto_sel and pagto_sel.get("data")
            else datetime.date.today()
        )
        data_pagto = st.date_input("Data", value=dt_padrao, format="DD/MM/YYYY")
    with col3:
        codpaciente = st.text_input(
            "Cód. Paciente",
            value=cod_paciente_val,
            disabled=True,
            help="Preenchido automaticamente",
        )
    with col4:
        paciente = st.text_input(
            "Nome do Paciente",
            value=nome_paciente_val,
            disabled=True,
            help="Preenchido automaticamente",
        )

    # Linha 2: Cód. Plano e Nome do Plano (Antes do campo vlrplano)
    col_p1, col_p2 = st.columns([1.2, 3])
    with col_p1:
        codplano = st.text_input(
            "Cód. Plano",
            value=cod_plano_val,
            disabled=True,
            help="Preenchido automaticamente a partir do plano selecionado",
        )
    with col_p2:
        plano = st.text_input(
            "Nome do Plano",
            value=nome_plano_val,
            disabled=True,
            help="Preenchido automaticamente a partir do plano selecionado",
        )

    # Linha 3: Valores e Tipo de Pagamento
    col5, col6, col7, col8 = st.columns([1, 1, 1, 1.5])
    with col5:
        vlrplano = st.number_input(
            "Vlr. Plano (R$)",
            value=float(pagto_sel.get("vlrplano", 0.0)) if pagto_sel else 0.0,
            min_value=0.0,
            step=10.0,
            format="%.2f",
        )
    with col6:
        vlrclinica = st.number_input(
            "Vlr. Clínica (R$)",
            value=float(pagto_sel.get("vlrclinica", 0.0)) if pagto_sel else 0.0,
            min_value=0.0,
            step=10.0,
            format="%.2f",
        )
    with col7:
        vlrfidelidade = st.number_input(
            "Vlr. Fidelidade (R$)",
            value=float(pagto_sel.get("vlrfidelidade", 0.0)) if pagto_sel else 0.0,
            min_value=0.0,
            step=10.0,
            format="%.2f",
        )
    with col8:
        tipos_opcao = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Transferência", "Boleto"]
        tipo_atual = pagto_sel.get("tipopagto", "Dinheiro") if pagto_sel else "Dinheiro"
        idx_tipo = tipos_opcao.index(tipo_atual) if tipo_atual in tipos_opcao else 0
        tipopagto = st.selectbox("Tipo de Pagamento", options=tipos_opcao, index=idx_tipo)

    st.markdown("<br>", unsafe_allow_html=True)

    # Botões de ação
    col15, col16, col17, col18 = st.columns(4)
    submit_criar = col15.form_submit_button("➕ Inserir", use_container_width=True)
    submit_atualizar = col16.form_submit_button("✏️ Atualizar", use_container_width=True)
    submit_deletar = col17.form_submit_button("🗑️ Deletar", use_container_width=True)
    submit_limpar = col18.form_submit_button("🧹 Limpar", use_container_width=True)

# ==========================================
# 7. Lógica de Persistência (CRUD)
# ==========================================
payload = {
    "codigo": codigo,
    "data": str(data_pagto),
    "codpaciente": codpaciente,
    "paciente": paciente,
    "codplano": codplano,
    "plano": plano,
    "vlrplano": vlrplano,
    "vlrclinica": vlrclinica,
    "vlrfidelidade": vlrfidelidade,
    "tipopagto": tipopagto,
}

# --- INSERIR ---
if submit_criar:
    if paciente and codpaciente:
        try:
            supabase.table("pagtofidelidade").insert(payload).execute()
            st.session_state["mensagem_sucesso"] = (
                f"Pagamento registrado com sucesso sob o Código {codigo}!"
            )
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir dados no banco: {e}")
    else:
        st.warning("Selecione um paciente válido na busca antes de gravar.")

# --- ATUALIZAR ---
if submit_atualizar:
    if id_ativo:
        try:
            supabase.table("pagtofidelidade").update(payload).eq("codigo", id_ativo).execute()
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
# 8. Pesquisa, Tabela e Download em PDF (Fora do Form)
# ==========================================
st.markdown("---")
st.markdown("##### 🔍 Localizar Pagamentos Fidelidade")

filtro = st.text_input("Filtrar por Paciente:", placeholder="Digite para buscar pelo nome do paciente...")
df_dados = carregar_dados(filtro)

if not df_dados.empty:
    colunas_exibicao = [
        c for c in [
            "codigo", "data", "codpaciente", "paciente",
            "codplano", "plano", "vlrplano", "vlrclinica",
            "vlrfidelidade", "tipopagto"
        ] if c in df_dados.columns
    ]

    evento_selecao = st.dataframe(
        df_dados[colunas_exibicao],
        column_config={
            "codigo": st.column_config.TextColumn("Código"),
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "codpaciente": st.column_config.TextColumn("Cód. Paciente"),
            "paciente": st.column_config.TextColumn("Paciente"),
            "codplano": st.column_config.TextColumn("Cód. Plano"),
            "plano": st.column_config.TextColumn("Plano"),
            "vlrplano": st.column_config.NumberColumn("Vlr. Plano", format="R$ %.2f"),
            "vlrclinica": st.column_config.NumberColumn("Vlr. Clínica", format="R$ %.2f"),
            "vlrfidelidade": st.column_config.NumberColumn("Vlr. Fidelidade", format="R$ %.2f"),
            "tipopagto": st.column_config.TextColumn("Tipo Pagto"),
        },
        selection_mode="single-row",
        on_select="rerun",
        use_container_width=True,
        key=f"tabela_pagtofidelidade_{st.session_state.table_key}",
        height=300,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    try:
        dados_clinica = obter_dados_clinica()
        pdf_data = gerar_relatorio_pdf(df_dados, dados_clinica)
        st.download_button(
            label="📄 Gerar Relatório PDF",
            data=pdf_data,
            file_name="relatorio_pagto_fidelidade.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Erro ao preparar arquivo PDF: {e}")

    linhas_selecionadas = evento_selecao.selection.get("rows", [])
    if linhas_selecionadas:
        indice_selecionado = linhas_selecionadas[0]
        dados_linha = df_dados.iloc[indice_selecionado].to_dict()

        if st.session_state.pagto_selecionado != dados_linha:
            st.session_state.pagto_selecionado = dados_linha
            st.rerun()
else:
    st.info("Nenhum pagamento registrado ou encontrado.")