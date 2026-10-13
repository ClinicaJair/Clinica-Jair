import io
import time
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import streamlit as st
from fpdf import FPDF
import base64
from supabase import Client, create_client

# ==========================================
# 1. Configuração da Página e Estilos
# ==========================================
st.set_page_config(page_title="Cadastro de Fichas Médicas", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    header { visibility: hidden; height: 0px; }

    /* Estilização dos Botões CRUD */
    div.stButton > button {
        background-color: #81D4FA !important;
        color: #000000 !important;
        border: 1px solid #4FC3F7 !important;
        font-weight: bold;
        transition: background-color 0.3s ease, border-color 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #4FC3F7 !important;
        color: #000000 !important;
        border-color: #0288D1 !important;
    }

    /* Estilização da Mensagem Centralizada */
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
# 3. Gerador de Relatório PDF Individual (Moderno e Profissional A4)
# ==========================================
class PDFRelatorioFichaIndividual(FPDF):
    def header(self):
        self.set_fill_color(2, 136, 209)
        self.rect(0, 0, 210, 15, 'F')
        self.set_font("helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 4)
        self.cell(190, 8, "SISTEMA DE GESTÃO MÉDICA - PRONTUÁRIO CLÍNICO", 0, 0, "C")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()} | Emitido em {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}", 0, 0, "C")


def gerar_relatorio_ficha_individual_pdf(ficha_dict):
    pdf = PDFRelatorioFichaIndividual(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def limpar(txt):
        if not txt:
            return ""
        return str(txt).encode("latin-1", "ignore").decode("latin-1")

    COLOR_PRIMARY = (2, 136, 209)
    COLOR_TEXT = (50, 50, 50)
    COLOR_BG_BOX = (245, 247, 250)

    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*COLOR_PRIMARY)
    num_ficha = ficha_dict.get("ficha", "N/A")
    data_cons = ficha_dict.get("dataconsulta", "")
    pdf.cell(130, 8, limpar(f"FICHA CLÍNICA N°: {num_ficha}"), 0, 0, "L")
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(60, 8, limpar(f"Data da Consulta: {data_cons}"), 0, 1, "R")

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(6)

    def desenhar_secao(titulo):
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(*COLOR_PRIMARY)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 6, f"   {titulo}", 0, 1, "L", fill=True)
        pdf.set_text_color(*COLOR_TEXT)
        pdf.ln(2)

    def campo_par(rotulo1, val1, rotulo2, val2, w1=93, w2=93):
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(35, 6, limpar(rotulo1), 0, 0, "L")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(w1 - 35, 6, limpar(val1), 0, 0, "L")

        pdf.set_font("helvetica", "B", 9)
        pdf.cell(30, 6, limpar(rotulo2), 0, 0, "L")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(w2 - 30, 6, limpar(val2), 0, 1, "L")

    desenhar_secao("DADOS DO PACIENTE")
    campo_par("Paciente:", ficha_dict.get("paciente", ""), "CPF:", ficha_dict.get("cpf", ""), 110, 80)
    campo_par("Endereço:", ficha_dict.get("endereco", ""), "Profissão:", ficha_dict.get("profissao", ""), 110, 80)
    campo_par("Telefone 1:", ficha_dict.get("telefone", ""), "Telefone 2:", ficha_dict.get("telefone1", ""), 110, 80)
    campo_par("Dt. Nascimento:", ficha_dict.get("datanascimento", ""), "Idade:", ficha_dict.get("idade", ""), 110, 80)
    pdf.ln(3)

    desenhar_secao("DADOS DO MÉDICO E ATENDIMENTO")
    campo_par("Médico:", ficha_dict.get("medico", ""), "Especialidade:", ficha_dict.get("especialidade", ""), 110, 80)
    valor_consulta = str(ficha_dict.get("especialidade_valor", ""))
    if valor_consulta and not valor_consulta.startswith("R$"):
        valor_consulta = f"R$ {valor_consulta}"
    campo_par("Valor Consulta:", valor_consulta, "", "", 110, 80)
    pdf.ln(3)

    desenhar_secao("AVALIAÇÃO CLÍNICA E REGISTROS")

    def bloco_texto(titulo_campo, conteudo):
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(190, 5, limpar(titulo_campo), 0, 1, "L")
        pdf.set_font("helvetica", "", 9)
        pdf.set_fill_color(*COLOR_BG_BOX)
        texto_tratado = limpar(conteudo) if conteudo else "Nenhum registro informado."
        pdf.multi_cell(190, 6, texto_tratado, border=1, fill=True, align="L")
        pdf.ln(3)

    bloco_texto("Quadro Principal:", ficha_dict.get("quadroprincipal", ""))
    bloco_texto("Histórico Atual:", ficha_dict.get("historicoatual", ""))
    bloco_texto("Histórico Principal:", ficha_dict.get("historicoprincipal", ""))
    bloco_texto("Exames:", ficha_dict.get("exames", ""))
    bloco_texto("Teste Realizado:", ficha_dict.get("testerealizado", ""))
    bloco_texto("Condutas:", ficha_dict.get("condutas", ""))
    bloco_texto("Evolução:", ficha_dict.get("evolucao", ""))

    return bytes(pdf.output())


# ==========================================
# 4. Funções Auxiliares e Sessão
# ==========================================
if "ficha_selecionada" not in st.session_state:
    st.session_state.ficha_selecionada = None
if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
if "table_key" not in st.session_state:
    st.session_state.table_key = 0
if "sel_paciente" not in st.session_state:
    st.session_state.sel_paciente = None
if "sel_medico" not in st.session_state:
    st.session_state.sel_medico = None


def limpar_campos_e_selecao():
    st.session_state.ficha_selecionada = None
    st.session_state.sel_paciente = None
    st.session_state.sel_medico = None
    st.session_state.update_trigger += 1
    st.session_state.table_key += 1


def calcular_idade(dt_nascimento):
    if not dt_nascimento:
        return ""
    try:
        if isinstance(dt_nascimento, str):
            dt_nasc = pd.to_datetime(dt_nascimento).date()
        elif isinstance(dt_nascimento, (datetime.date, datetime.datetime)):
            dt_nasc = dt_nascimento
        else:
            return ""

        hoje = datetime.date.today()
        diferenca = relativedelta(hoje, dt_nasc)

        if diferenca.years > 0:
            return f"{diferenca.years} anos"
        elif diferenca.months > 0:
            return f"{diferenca.months} meses"
        else:
            return f"{diferenca.days} dias"
    except Exception:
        return ""


def carregar_dados(pesquisa=""):
    try:
        if pesquisa:
            response = (
                supabase.table("fichas")
                .select("*")
                .ilike("paciente", f"%{pesquisa}%")
                .execute()
            )
        else:
            response = supabase.table("fichas").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela fichas: {e}")
        return pd.DataFrame()


def carregar_pacientes_dados():
    try:
        response = supabase.table("pacientes").select(
            "nome, endereco, profissao, cpf, telefone, telefone1, data_nascimento"
        ).order("nome").execute()

        if response.data:
            dict_pacientes = {}
            for item in response.data:
                if item.get("nome"):
                    nome_clean = item["nome"].strip()
                    dict_pacientes[nome_clean] = item
            return dict_pacientes
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar pacientes: {e}")
        return {}


def carregar_medicos_e_especialidades():
    try:
        response = supabase.table("medicos").select("nome, especialidade, especialidade_valor").order("nome").execute()
        if response.data:
            dict_medicos = {}
            for item in response.data:
                if item.get("nome"):
                    nome_clean = item["nome"].strip()
                    dict_medicos[nome_clean] = {
                        "especialidade": item.get("especialidade", ""),
                        "especialidade_valor": item.get("especialidade_valor", "")
                    }
            return dict_medicos
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar médicos: {e}")
        return {}


def obter_proxima_ficha():
    try:
        res = (
            supabase.table("fichas")
            .select("ficha")
            .order("ficha", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            ultima_ficha = res.data[0]["ficha"]
            try:
                return int(ultima_ficha) + 1
            except (ValueError, TypeError):
                return 1
        return 1
    except Exception:
        return 1


@st.dialog("⚠️ Confirmar Exclusão")
def dialog_confirmar_deletar(ficha_deletar):
    st.write(f"Deseja realmente deletar a **Ficha {ficha_deletar}**?")
    col_sim, col_nao = st.columns(2)

    with col_sim:
        if st.button("Sim", use_container_width=True, type="primary"):
            try:
                supabase.table("fichas").delete().eq("ficha", ficha_deletar).execute()
                limpar_campos_e_selecao()
                st.session_state["mensagem_sucesso"] = "Ficha removida com sucesso!"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao deletar ficha: {e}")

    with col_nao:
        if st.button("Não", use_container_width=True):
            st.rerun()


# ==========================================
# 5. Exibição da Mensagem Temporária Centralizada
# ==========================================
if "mensagem_sucesso" in st.session_state:
    mensagem = st.session_state.pop("mensagem_sucesso")
    container_msg = st.empty()
    container_msg.markdown(
        f'<div class="mensagem-centralizada">✅ {mensagem}</div>',
        unsafe_allow_html=True
    )
    time.sleep(3)
    container_msg.empty()

st.markdown("### 🏥 Gestão de Fichas Médicas")

# Carregamento prévio de listas auxiliares
dict_pacientes = carregar_pacientes_dados()
lista_pacientes = list(dict_pacientes.keys())

dict_medicos = carregar_medicos_e_especialidades()
lista_medicos = list(dict_medicos.keys())

# Preparação do estado da ficha selecionada
ficha_sel = st.session_state.ficha_selecionada

if ficha_sel:
    pac_sel = (ficha_sel.get("paciente") or "").strip()
    med_sel = (ficha_sel.get("medico") or "").strip()

    st.session_state.sel_paciente = pac_sel
    st.session_state.sel_medico = med_sel

    if pac_sel and pac_sel not in lista_pacientes:
        lista_pacientes.insert(0, pac_sel)
    if med_sel and med_sel not in lista_medicos:
        lista_medicos.insert(0, med_sel)

id_ativo = ficha_sel.get("ficha") if ficha_sel else None

# ==========================================
# Chaves e Callbacks Dinâmicos do Paciente
# ==========================================
trigger = st.session_state.update_trigger
pac_key = f"paciente_select_{trigger}"
end_key = f"end_{trigger}"
prof_key = f"prof_{trigger}"
cpf_key = f"cpf_{trigger}"
tel_key = f"tel_{trigger}"
tel1_key = f"tel1_{trigger}"
dtnasc_key = f"dtnasc_{trigger}"
idade_key = f"idade_{trigger}"


def ao_mudar_paciente():
    paciente_escolhido = st.session_state.get(pac_key)
    dados_p = dict_pacientes.get(paciente_escolhido, {}) if paciente_escolhido else {}

    st.session_state[end_key] = dados_p.get("endereco", "")
    st.session_state[prof_key] = dados_p.get("profissao", "")
    st.session_state[cpf_key] = dados_p.get("cpf", "")
    st.session_state[tel_key] = dados_p.get("telefone", "")
    st.session_state[tel1_key] = dados_p.get("telefone1", "")

    dt_nasc_str = dados_p.get("data_nascimento")
    if dt_nasc_str:
        try:
            st.session_state[dtnasc_key] = pd.to_datetime(dt_nasc_str).date()
            st.session_state[idade_key] = calcular_idade(st.session_state[dtnasc_key])
        except Exception:
            st.session_state[idade_key] = ""
    else:
        st.session_state[idade_key] = ""


# Se houver ficha selecionada, define valores iniciais nos estados dos inputs complementares
if ficha_sel:
    if end_key not in st.session_state:
        st.session_state[end_key] = ficha_sel.get("endereco") if ficha_sel.get("endereco") is not None else dict_pacientes.get(
            ficha_sel.get("paciente"), {}).get("endereco", "")
    if prof_key not in st.session_state:
        st.session_state[prof_key] = ficha_sel.get("profissao") if ficha_sel.get("profissao") is not None else dict_pacientes.get(
            ficha_sel.get("paciente"), {}).get("profissao", "")
    if cpf_key not in st.session_state:
        st.session_state[cpf_key] = ficha_sel.get("cpf") if ficha_sel.get("cpf") is not None else dict_pacientes.get(
            ficha_sel.get("paciente"), {}).get("cpf", "")
    if tel_key not in st.session_state:
        st.session_state[tel_key] = ficha_sel.get("telefone") if ficha_sel.get("telefone") is not None else dict_pacientes.get(
            ficha_sel.get("paciente"), {}).get("telefone", "")
    if tel1_key not in st.session_state:
        st.session_state[tel1_key] = ficha_sel.get("telefone1") if ficha_sel.get("telefone1") is not None else dict_pacientes.get(
            ficha_sel.get("paciente"), {}).get("telefone1", "")

    dt_nasc_raw = ficha_sel.get("datanascimento") or ficha_sel.get("data_nascimento") or dict_pacientes.get(ficha_sel.get("paciente"),
                                                                                                            {}).get("data_nascimento")
    if dtnasc_key not in st.session_state:
        try:
            st.session_state[dtnasc_key] = pd.to_datetime(dt_nasc_raw).date() if dt_nasc_raw else None
        except Exception:
            st.session_state[dtnasc_key] = None
    if idade_key not in st.session_state:
        st.session_state[idade_key] = ficha_sel.get("idade") if ficha_sel.get("idade") else calcular_idade(st.session_state.get(dtnasc_key))
else:
    dados_paciente_inicial = dict_pacientes.get(st.session_state.sel_paciente, {}) if st.session_state.sel_paciente else {}
    if end_key not in st.session_state:
        st.session_state[end_key] = dados_paciente_inicial.get("endereco", "")
    if prof_key not in st.session_state:
        st.session_state[prof_key] = dados_paciente_inicial.get("profissao", "")
    if cpf_key not in st.session_state:
        st.session_state[cpf_key] = dados_paciente_inicial.get("cpf", "")
    if tel_key not in st.session_state:
        st.session_state[tel_key] = dados_paciente_inicial.get("telefone", "")
    if tel1_key not in st.session_state:
        st.session_state[tel1_key] = dados_paciente_inicial.get("telefone1", "")
    if dtnasc_key not in st.session_state:
        dt_nasc_i = dados_paciente_inicial.get("data_nascimento")
        try:
            st.session_state[dtnasc_key] = pd.to_datetime(dt_nasc_i).date() if dt_nasc_i else None
        except Exception:
            st.session_state[dtnasc_key] = None
    if idade_key not in st.session_state:
        st.session_state[idade_key] = calcular_idade(st.session_state.get(dtnasc_key))

# ==========================================
# 6. PARTE SUPERIOR (Campos Ficha, Dt Consulta e Paciente em uma única linha)
# ==========================================
col_sup_1, col_sup_2, col_sup_3 = st.columns([1.5, 1.5, 3.5])

with col_sup_1:
    ficha_exibicao = int(id_ativo) if id_ativo else obter_proxima_ficha()
    num_ficha = st.number_input(
        "Ficha", value=ficha_exibicao, disabled=True, help="Gerado automaticamente"
    )

with col_sup_2:
    data_consulta_init = datetime.date.today()
    if ficha_sel and ficha_sel.get("dataconsulta"):
        try:
            data_consulta_init = pd.to_datetime(ficha_sel["dataconsulta"]).date()
        except Exception:
            pass

    dataconsulta_val = st.date_input(
        "Dt. Consulta",
        value=data_consulta_init,
        format="DD/MM/YYYY",
        key=f"dataconsulta_{trigger}"
    )

with col_sup_3:
    idx_paciente = None
    if st.session_state.sel_paciente in lista_pacientes:
        idx_paciente = lista_pacientes.index(st.session_state.sel_paciente)

    paciente = st.selectbox(
        "Paciente *",
        options=lista_pacientes,
        index=idx_paciente,
        placeholder="Selecione um paciente...",
        key=pac_key,
        on_change=ao_mudar_paciente
    )
    st.session_state.sel_paciente = paciente

# ==========================================
# 7. Interface Gráfica com Abas (Tabs)
# ==========================================
tab_pac_med, tab_clinica, tab_localizacao = st.tabs([
    "👤 Dados Médico / Paciente",
    "📋 Avaliação Clínica",
    "🔍 Localização das Fichas"
])

# ------------------------------------------
# ABA 1: Dados do Médico e do Paciente
# ------------------------------------------
with tab_pac_med:
    st.markdown("##### 🩺 Dados do Médico")
    med_key = f"medico_select_{trigger}"
    esp_key = f"especialidade_input_{trigger}"
    val_key = f"especialidade_valor_input_{trigger}"


    def ao_mudar_medico():
        medico_escolhido = st.session_state.get(med_key)
        dados_m = dict_medicos.get(medico_escolhido, {}) if medico_escolhido else {}
        st.session_state[esp_key] = dados_m.get("especialidade", "")
        st.session_state[val_key] = str(dados_m.get("especialidade_valor", "")) if dados_m.get("especialidade_valor") is not None else ""


    if ficha_sel:
        if "especialidade" in ficha_sel:
            st.session_state[esp_key] = ficha_sel.get("especialidade", "")
        if "especialidade_valor" in ficha_sel:
            st.session_state[val_key] = str(ficha_sel.get("especialidade_valor", ""))
    elif st.session_state.sel_medico in dict_medicos:
        dados_med_ativo = dict_medicos[st.session_state.sel_medico]
        if esp_key not in st.session_state:
            st.session_state[esp_key] = dados_med_ativo.get("especialidade", "")
        if val_key not in st.session_state:
            st.session_state[val_key] = str(dados_med_ativo.get("especialidade_valor", ""))
    else:
        if esp_key not in st.session_state:
            st.session_state[esp_key] = ""
        if val_key not in st.session_state:
            st.session_state[val_key] = ""

    col_med1, col_med2, col_med3 = st.columns([2.5, 2.0, 1.5])
    with col_med1:
        idx_medico = None
        if st.session_state.sel_medico in lista_medicos:
            idx_medico = lista_medicos.index(st.session_state.sel_medico)

        medico = st.selectbox(
            "Médico *",
            options=lista_medicos,
            index=idx_medico,
            placeholder="Selecione um médico...",
            key=med_key,
            on_change=ao_mudar_medico
        )
        st.session_state.sel_medico = medico

    with col_med2:
        especialidade = st.text_input(
            "Especialidade",
            disabled=True,
            help="Preenchido automaticamente",
            key=esp_key
        )

    with col_med3:
        especialidade_valor = st.text_input(
            "Valor Consulta",
            disabled=True,
            help="Preenchido automaticamente",
            key=val_key
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 👤 Dados Complementares do Paciente")

    col_p1, col_p2, col_p3 = st.columns([2.5, 1.5, 1.5])
    with col_p1:
        endereco = st.text_input("Endereço", max_chars=100, key=end_key)
    with col_p2:
        profissao = st.text_input("Profissão", max_chars=20, key=prof_key)
    with col_p3:
        cpf = st.text_input("CPF", max_chars=20, key=cpf_key)

    col_p4, col_p5, col_p6, col_p7 = st.columns([1.5, 1.5, 1.5, 1])
    with col_p4:
        telefone = st.text_input("Telefone 1", max_chars=20, key=tel_key)
    with col_p5:
        telefone1 = st.text_input("Telefone 2", max_chars=20, key=tel1_key)
    with col_p6:
        datanascimento_val = st.date_input(
            "Dt. Nascimento",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            format="DD/MM/YYYY",
            key=dtnasc_key
        )
    with col_p7:
        # Atualiza a idade automaticamente baseada na data de nascimento do input
        if st.session_state.get(dtnasc_key):
            st.session_state[idade_key] = calcular_idade(st.session_state[dtnasc_key])
        idade = st.text_input("Idade", max_chars=20, key=idade_key)

# ------------------------------------------
# ABA 2: Avaliação Clínica
# ------------------------------------------
with tab_clinica:
    st.markdown("##### 📝 Registros Clínicos")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        quadroprincipal = st.text_area(
            "Quadro Principal", value=ficha_sel.get("quadroprincipal", "") if ficha_sel else "", max_chars=200, height=80,
            key=f"qp_{trigger}"
        )
    with col_c2:
        historicoatual = st.text_area(
            "Histórico Atual", value=ficha_sel.get("historicoatual", "") if ficha_sel else "", max_chars=200, height=80, key=f"ha_{trigger}"
        )

    col_c3, col_c4 = st.columns(2)
    with col_c3:
        historicoprincipal = st.text_area(
            "Histórico Principal", value=ficha_sel.get("historicoprincipal", "") if ficha_sel else "", max_chars=200, height=80,
            key=f"hp_{trigger}"
        )
    with col_c4:
        exames = st.text_area(
            "Exames", value=ficha_sel.get("exames", "") if ficha_sel else "", max_chars=200, height=80, key=f"ex_{trigger}"
        )

    col_c5, col_c6, col_c7 = st.columns(3)
    with col_c5:
        testerealizado = st.text_area(
            "Teste Realizado", value=ficha_sel.get("testerealizado", "") if ficha_sel else "", max_chars=200, height=80, key=f"tr_{trigger}"
        )
    with col_c6:
        condutas = st.text_area(
            "Condutas", value=ficha_sel.get("condutas", "") if ficha_sel else "", max_chars=200, height=80, key=f"cd_{trigger}"
        )
    with col_c7:
        evolucao = st.text_area(
            "Evolução", value=ficha_sel.get("evolucao", "") if ficha_sel else "", max_chars=200, height=80, key=f"ev_{trigger}"
        )

# ------------------------------------------
# ABA 3: Localização das Fichas e Relatório/Impressão
# ------------------------------------------
with tab_localizacao:
    st.markdown("##### 🔍 Localizar Ficha")
    filtro = st.text_input(
        "Filtrar por Paciente:", placeholder="Digite para buscar...", key=f"filtro_{st.session_state.table_key}"
    )
    df_dados = carregar_dados(filtro)

    if not df_dados.empty:
        colunas_exibicao = [
            c for c in ["ficha", "paciente", "medico", "dataconsulta"] if c in df_dados.columns
        ]

        evento_selecao = st.dataframe(
            df_dados[colunas_exibicao],
            selection_mode="single-row",
            on_select="rerun",
            use_container_width=True,
            key=f"tabela_fichas_{st.session_state.table_key}",
            height=260,
        )

        linhas_selecionadas = evento_selecao.selection.get("rows", [])
        if linhas_selecionadas:
            indice_selecionado = linhas_selecionadas[0]
            dados_linha = df_dados.iloc[indice_selecionado].to_dict()

            if st.session_state.ficha_selecionada != dados_linha:
                st.session_state.ficha_selecionada = dados_linha
                st.session_state.update_trigger += 1
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.ficha_selecionada:
            ficha_atual_dict = st.session_state.ficha_selecionada
            num_ficha_sel = ficha_atual_dict.get('ficha')
            nome_pac_sel = ficha_atual_dict.get('paciente', 'paciente')

            st.markdown(f"**📌 Ficha Selecionada para Relatório / Impressão:** N° {num_ficha_sel} — **{nome_pac_sel}**")

            try:
                pdf_bytes = gerar_relatorio_ficha_individual_pdf(ficha_atual_dict)
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

                col_down, col_print = st.columns(2)

                with col_down:
                    st.download_button(
                        label="📄 Baixar Relatório PDF A4",
                        data=pdf_bytes,
                        file_name=f"ficha_{num_ficha_sel}_{nome_pac_sel.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                with col_print:
                    html_botao_imprimir = f"""
                    <script>
                    function imprimirPDF_{num_ficha_sel}() {{
                        var pdfWindow = window.open("");
                        pdfWindow.document.write(
                            '<iframe width="100%" height="100%" src="data:application/pdf;base64,{b64_pdf}"></iframe>'
                        );
                        setTimeout(function() {{
                            pdfWindow.print();
                        }}, 1000);
                    }}
                    </script>
                    <button onclick="imprimirPDF_{num_ficha_sel}()" style="
                        width: 100%;
                        background-color: #81D4FA;
                        color: black;
                        border: 1px solid #4FC3F7;
                        padding: 0.55rem 1rem;
                        font-weight: bold;
                        border-radius: 0.25rem;
                        cursor: pointer;
                        text-align: center;
                    ">
                        🖨️ Imprimir Ficha A4
                    </button>
                    """
                    st.components.v1.html(html_botao_imprimir, height=45)

            except Exception as e:
                st.error(f"Erro ao gerar relatório da ficha: {e}")
        else:
            st.info("💡 Clique em uma linha da tabela acima para habilitar o relatório individual e as opções de impressão.")

    else:
        st.info("Nenhuma ficha cadastrada ou encontrada.")

# ==========================================
# 8. BOTÕES CRUD ABAIXO DAS ABAS
# ==========================================
st.markdown("---")
col_crud1, col_crud2, col_crud3, col_crud4 = st.columns(4)

btn_inserir = col_crud1.button("➕ Inserir", use_container_width=True)
btn_atualizar = col_crud2.button("✏️ Atualizar", use_container_width=True)
btn_deletar = col_crud3.button("🗑️ Deletar", use_container_width=True)
btn_limpar = col_crud4.button("🧹 Limpar", use_container_width=True)

# ==========================================
# 9. Lógica de Persistência e Consistência (CRUD)
# ==========================================
dataconsulta_str = dataconsulta_val.strftime("%Y-%m-%d") if dataconsulta_val else None
datanascimento_str = st.session_state.get(dtnasc_key).strftime("%Y-%m-%d") if st.session_state.get(dtnasc_key) else None

dados_medico_sel = dict_medicos.get(medico, {})
especialidade_salvar = st.session_state.get(esp_key) or dados_medico_sel.get("especialidade", "")
especialidade_valor_salvar = st.session_state.get(val_key) or dados_medico_sel.get("especialidade_valor", "")

payload = {
    "ficha": num_ficha,
    "dataconsulta": dataconsulta_str,
    "paciente": paciente,
    "endereco": st.session_state.get(end_key, ""),
    "profissao": st.session_state.get(prof_key, ""),
    "cpf": st.session_state.get(cpf_key, ""),
    "telefone": st.session_state.get(tel_key, ""),
    "telefone1": st.session_state.get(tel1_key, ""),
    "datanascimento": datanascimento_str,
    "idade": st.session_state.get(idade_key, ""),
    "medico": medico,
    "especialidade": especialidade_salvar,
    "especialidade_valor": especialidade_valor_salvar,
    "quadroprincipal": quadroprincipal,
    "historicoatual": historicoatual,
    "historicoprincipal": historicoprincipal,
    "exames": exames,
    "testerealizado": testerealizado,
    "condutas": condutas,
    "evolucao": evolucao,
}

if btn_inserir:
    if id_ativo:
        st.warning("Você está editando uma ficha existente. Para cadastrar uma nova ficha, clique em '🧹 Limpar' primeiro.")
    elif not paciente or not medico:
        st.warning("Preencha obrigatoriamente os campos 'Paciente' e 'Médico'.")
    else:
        try:
            supabase.table("fichas").insert(payload).execute()
            st.session_state["mensagem_sucesso"] = f"Ficha N° {num_ficha} cadastrada com sucesso!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir ficha no banco: {e}")

if btn_atualizar:
    if not id_ativo:
        st.warning("Selecione uma ficha existente na aba 'Localização das Fichas' antes de atualizar.")
    elif not paciente or not medico:
        st.warning("Os campos 'Paciente' e 'Médico' são obrigatórios.")
    else:
        try:
            supabase.table("fichas").update(payload).eq("ficha", id_ativo).execute()
            st.session_state["mensagem_sucesso"] = f"Ficha N° {id_ativo} atualizada com sucesso!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar ficha: {e}")

if btn_deletar:
    if not id_ativo:
        st.warning("Selecione uma ficha na aba 'Localização das Fichas' antes de tentar deletar.")
    else:
        dialog_confirmar_deletar(id_ativo)

if btn_limpar:
    limpar_campos_e_slecao = limpar_campos_e_selecao()
    st.rerun()