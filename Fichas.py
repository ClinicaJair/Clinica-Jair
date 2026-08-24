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
st.set_page_config(page_title="Cadastro de Fichas Médicas", layout="wide")

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
    pdf.cell(0, 8, limpar_texto("SISTEMA DE GESTÃO MÉDICA"), ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        0,
        6,
        limpar_texto("Relatório Geral de Fichas Médicas"),
        ln=True,
        align="C",
    )

    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, 26, 200, 26)
    pdf.ln(8)

    # --- CABEÇALHO DA TABELA ---
    largura_ficha = 25
    largura_paciente = 70
    largura_medico = 55
    largura_data = 40

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(largura_ficha, 8, limpar_texto(" Ficha"), border=1, fill=True)
    pdf.cell(largura_paciente, 8, limpar_texto(" Paciente"), border=1, fill=True)
    pdf.cell(largura_medico, 8, limpar_texto(" Médico"), border=1, fill=True)
    pdf.cell(largura_data, 8, limpar_texto(" Data Consulta"), border=1, ln=True, fill=True)

    # --- DADOS DA TABELA ---
    pdf.set_font("helvetica", "", 9)

    for _, row in df.iterrows():
        ficha = limpar_texto(row.get("ficha", "")) if pd.notna(row.get("ficha")) else ""
        paciente = limpar_texto(row.get("paciente", "")) if pd.notna(row.get("paciente")) else ""
        medico = limpar_texto(row.get("medico", "")) if pd.notna(row.get("medico")) else ""
        dataconsulta = limpar_texto(row.get("dataconsulta", "")) if pd.notna(row.get("dataconsulta")) else ""

        if len(paciente) > 35:
            paciente = paciente[:32] + "..."
        if len(medico) > 28:
            medico = medico[:25] + "..."

        pdf.cell(largura_ficha, 7, f" {ficha}", border=1)
        pdf.cell(largura_paciente, 7, f" {paciente}", border=1)
        pdf.cell(largura_medico, 7, f" {medico}", border=1)
        pdf.cell(largura_data, 7, f" {dataconsulta}", border=1, ln=True)

    return bytes(pdf.output())


# ==========================================
# 4. Inicialização do Session State e Funções
# ==========================================
if "ficha_selecionada" not in st.session_state:
    st.session_state.ficha_selecionada = None
if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
if "table_key" not in st.session_state:
    st.session_state.table_key = 0

# Estados para controlar seleções de paciente e médico
if "sel_paciente" not in st.session_state:
    st.session_state.sel_paciente = None
if "sel_medico" not in st.session_state:
    st.session_state.sel_medico = None


def limpar_campos_e_selecao():
    """Reseta a ficha selecionada e força novas chaves para o formulário e a tabela."""
    st.session_state.ficha_selecionada = None
    st.session_state.sel_paciente = None
    st.session_state.sel_medico = None
    st.session_state.update_trigger += 1
    st.session_state.table_key += 1


def calcular_idade(dt_nascimento):
    """Calcula a idade exata com base na data de nascimento e data atual."""
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
    """Busca a lista de pacientes e seus dados completos cadastrados na tabela 'pacientes'."""
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
    """Busca médicos e suas respectivas especialidades na tabela 'medicos'."""
    try:
        response = supabase.table("medicos").select("nome, especialidade").order("nome").execute()
        if response.data:
            dict_medicos = {}
            for item in response.data:
                if item.get("nome"):
                    nome_clean = item["nome"].strip()
                    dict_medicos[nome_clean] = item.get("especialidade", "")
            return dict_medicos
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar médicos: {e}")
        return {}


def obter_proxima_ficha():
    """Busca o maior número de ficha cadastrado no Supabase e retorna o próximo valor."""
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


# Modal de Confirmação para Deletar
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
# EXIBIÇÃO DA MENSAGEM TEMPORÁRIA CENTRALIZADA
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

st.subheader("📋 Gestão de Fichas Médicas")

# Carregamento prévio de listas de pacientes e médicos
dict_pacientes = carregar_pacientes_dados()
lista_pacientes = list(dict_pacientes.keys())

dict_medicos = carregar_medicos_e_especialidades()
lista_medicos = list(dict_medicos.keys())

# ==========================================
# PREPARAÇÃO E COMPATIBILIDADE DOS DADOS
# ==========================================
ficha_sel = st.session_state.ficha_selecionada

if ficha_sel:
    pac_sel = (ficha_sel.get("paciente") or "").strip()
    med_sel = (ficha_sel.get("medico") or "").strip()

    st.session_state.sel_paciente = pac_sel
    st.session_state.sel_medico = med_sel

    # Garante inclusão de dados da ficha nas listas ativas do combobox se não existirem nas tabelas secundárias
    if pac_sel and pac_sel not in lista_pacientes:
        lista_pacientes.insert(0, pac_sel)
    if med_sel and med_sel not in lista_medicos:
        lista_medicos.insert(0, med_sel)

id_ativo = ficha_sel.get("ficha") if ficha_sel else None

# ==========================================
# 5. Interface Gráfica em Duas Colunas
# ==========================================
col_esquerda, col_direita = st.columns([1.7, 1.3])

# ------------------------------------------
# COLUNA ESQUERDA: Formulário de Cadastro e Edição
# ------------------------------------------
with col_esquerda:
    if id_ativo:
        st.markdown(f"##### ✏️ Editando Ficha: N° {id_ativo}")
        ficha_exibicao = int(id_ativo)
    else:
        st.markdown("##### ➕ Nova Ficha")
        ficha_exibicao = obter_proxima_ficha()

    # --- SELETORES REATIVOS (Fora do st.form) ---
    col1, col2, col3 = st.columns([1, 1.5, 3.5])
    with col1:
        num_ficha = st.number_input(
            "Ficha", value=ficha_exibicao, disabled=True, help="Gerado automaticamente"
        )
    with col2:
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
            key=f"dataconsulta_{st.session_state.update_trigger}"
        )
    with col3:
        idx_paciente = None
        if st.session_state.sel_paciente in lista_pacientes:
            idx_paciente = lista_pacientes.index(st.session_state.sel_paciente)

        paciente = st.selectbox(
            "Paciente",
            options=lista_pacientes,
            index=idx_paciente,
            placeholder="Selecione um paciente...",
            key=f"paciente_select_{st.session_state.update_trigger}"
        )
        st.session_state.sel_paciente = paciente

    # Busca os dados do paciente selecionado no dicionário auxiliar
    dados_paciente_sel = dict_pacientes.get(paciente, {}) if paciente else {}

    # Define valores dos campos priorizando os dados da ficha ativa ou da tabela de pacientes
    if ficha_sel:
        end_val = ficha_sel.get("endereco") if ficha_sel.get("endereco") is not None else dados_paciente_sel.get("endereco", "")
        prof_val = ficha_sel.get("profissao") if ficha_sel.get("profissao") is not None else dados_paciente_sel.get("profissao", "")
        cpf_val = ficha_sel.get("cpf") if ficha_sel.get("cpf") is not None else dados_paciente_sel.get("cpf", "")
        tel_val = ficha_sel.get("telefone") if ficha_sel.get("telefone") is not None else dados_paciente_sel.get("telefone", "")
        tel1_val = ficha_sel.get("telefone1") if ficha_sel.get("telefone1") is not None else dados_paciente_sel.get("telefone1", "")
        dt_nasc_raw = ficha_sel.get("datanascimento") or ficha_sel.get("data_nascimento") or dados_paciente_sel.get("data_nascimento")
    else:
        end_val = dados_paciente_sel.get("endereco", "")
        prof_val = dados_paciente_sel.get("profissao", "")
        cpf_val = dados_paciente_sel.get("cpf", "")
        tel_val = dados_paciente_sel.get("telefone", "")
        tel1_val = dados_paciente_sel.get("telefone1", "")
        dt_nasc_raw = dados_paciente_sel.get("data_nascimento")

    dt_nasc_init = None
    if dt_nasc_raw:
        try:
            dt_nasc_init = pd.to_datetime(dt_nasc_raw).date()
        except Exception:
            dt_nasc_init = None

    idade_calc = ficha_sel.get("idade") if ficha_sel else calcular_idade(dt_nasc_init)

    # --- SELEÇÃO DE MÉDICO E ESPECIALIDADE ---
    trigger = st.session_state.update_trigger
    med_key = f"medico_select_{trigger}"
    esp_key = f"especialidade_input_{trigger}"

    def ao_mudar_medico():
        medico_escolhido = st.session_state.get(med_key)
        nova_esp = dict_medicos.get(medico_escolhido, "") if medico_escolhido else ""
        st.session_state[esp_key] = nova_esp

    # Atualiza a chave de especialidade dinamicamente no estado
    if ficha_sel and ficha_sel.get("especialidade"):
        st.session_state[esp_key] = ficha_sel.get("especialidade")
    elif st.session_state.sel_medico in dict_medicos:
        st.session_state[esp_key] = dict_medicos[st.session_state.sel_medico]
    elif esp_key not in st.session_state:
        st.session_state[esp_key] = ""

    col_med1, col_med2 = st.columns([2.5, 2.5])
    with col_med1:
        idx_medico = None
        if st.session_state.sel_medico in lista_medicos:
            idx_medico = lista_medicos.index(st.session_state.sel_medico)

        medico = st.selectbox(
            "Médico",
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
            help="Preenchido automaticamente a partir da tabela de médicos",
            key=esp_key
        )

    # --- FORMULÁRIO DE DADOS ADICIONAIS E CONFIRMAÇÃO ---
    with st.form(key=f"form_ficha_{trigger}"):

        # Linha 2: Endereço, Profissão e CPF
        col4, col5, col6 = st.columns([2.5, 1.5, 1.5])
        with col4:
            endereco = st.text_input("Endereço", value=end_val or "", max_chars=100)
        with col5:
            profissao = st.text_input("Profissão", value=prof_val or "", max_chars=20)
        with col6:
            cpf = st.text_input("CPF", value=cpf_val or "", max_chars=20)

        # Linha 3: Telefones, Dt. Nascimento e Idade
        col7, col8, col9, col10 = st.columns([1.5, 1.5, 1.5, 1])
        with col7:
            telefone = st.text_input("Telefone 1", value=tel_val or "", max_chars=20)
        with col8:
            telefone1 = st.text_input("Telefone 2", value=tel1_val or "", max_chars=20)
        with col9:
            datanascimento_val = st.date_input(
                "Dt. Nascimento",
                value=dt_nasc_init,
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today(),
                format="DD/MM/YYYY"
            )
        with col10:
            idade_exibicao = calcular_idade(datanascimento_val) if datanascimento_val else idade_calc
            idade = st.text_input("Idade", value=idade_exibicao or "", max_chars=20)

        # Linha 5: Avaliações Clínicas I
        col13, col14 = st.columns(2)
        with col13:
            quadroprincipal = st.text_area(
                "Quadro Principal", value=ficha_sel.get("quadroprincipal", "") if ficha_sel else "", max_chars=200, height=70
            )
        with col14:
            historicoatual = st.text_area(
                "Histórico Atual", value=ficha_sel.get("historicoatual", "") if ficha_sel else "", max_chars=200, height=70
            )

        # Linha 6: Avaliações Clínicas II
        col15, col16 = st.columns(2)
        with col15:
            historicoprincipal = st.text_area(
                "Histórico Principal", value=ficha_sel.get("historicoprincipal", "") if ficha_sel else "", max_chars=200, height=70
            )
        with col16:
            exames = st.text_area(
                "Exames", value=ficha_sel.get("exames", "") if ficha_sel else "", max_chars=200, height=70
            )

        # Linha 7: Avaliações Clínicas III
        col17, col18, col19 = st.columns(3)
        with col17:
            testerealizado = st.text_area(
                "Teste Realizado", value=ficha_sel.get("testerealizado", "") if ficha_sel else "", max_chars=200, height=70
            )
        with col18:
            condutas = st.text_area(
                "Condutas", value=ficha_sel.get("condutas", "") if ficha_sel else "", max_chars=200, height=70
            )
        with col19:
            evolucao = st.text_area(
                "Evolução", value=ficha_sel.get("evolucao", "") if ficha_sel else "", max_chars=200, height=70
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Botões de ação do formulário
        col20, col21, col22, col23 = st.columns(4)
        submit_criar = col20.form_submit_button(
            "➕ Inserir", use_container_width=True
        )
        submit_atualizar = col21.form_submit_button(
            "✏️ Atualizar", use_container_width=True
        )
        submit_deletar = col22.form_submit_button(
            "🗑️ Deletar", use_container_width=True
        )
        submit_limpar = col23.form_submit_button(
            "🧹 Limpar", use_container_width=True
        )

# ------------------------------------------
# COLUNA DIREITA: Pesquisa e Seleção (Processada antes do rerun)
# ------------------------------------------
with col_direita:
    st.markdown("##### 🔍 Localizar Ficha")
    filtro = st.text_input(
        "Filtrar por Paciente:", placeholder="Digite para buscar..."
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
            height=580,
        )

        # --- PROCESSA A SELEÇÃO DA TABELA ---
        linhas_selecionadas = evento_selecao.selection.get("rows", [])
        if linhas_selecionadas:
            indice_selecionado = linhas_selecionadas[0]
            dados_linha = df_dados.iloc[indice_selecionado].to_dict()

            # Força a atualização do estado e um rerun imediato se for uma nova linha selecionada
            if st.session_state.ficha_selecionada != dados_linha:
                st.session_state.ficha_selecionada = dados_linha
                st.session_state.update_trigger += 1
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        try:
            pdf_data = gerar_relatorio_pdf(df_dados)
            st.download_button(
                label="📄 Gerar Relatório PDF",
                data=pdf_data,
                file_name="relatorio_fichas.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Erro ao preparar arquivo PDF: {e}")

    else:
        st.info("Nenhuma ficha cadastrada ou encontrada.")

# ==========================================
# 6. Lógica de Persistência (CRUD) e Ações
# ==========================================
dataconsulta_str = dataconsulta_val.strftime("%Y-%m-%d") if dataconsulta_val else None
datanascimento_str = datanascimento_val.strftime("%Y-%m-%d") if datanascimento_val else None

especialidade_salvar = st.session_state.get(esp_key) or dict_medicos.get(medico, "")

payload = {
    "ficha": num_ficha,
    "dataconsulta": dataconsulta_str,
    "paciente": paciente,
    "endereco": endereco,
    "profissao": profissao,
    "cpf": cpf,
    "telefone": telefone,
    "telefone1": telefone1,
    "datanascimento": datanascimento_str,
    "idade": idade,
    "medico": medico,
    "especialidade": especialidade_salvar,
    "quadroprincipal": quadroprincipal,
    "historicoatual": historicoatual,
    "historicoprincipal": historicoprincipal,
    "exames": exames,
    "testerealizado": testerealizado,
    "condutas": condutas,
    "evolucao": evolucao,
}

# --- INSERIR ---
if submit_criar:
    if paciente and medico:
        try:
            supabase.table("fichas").insert(payload).execute()
            st.session_state["mensagem_sucesso"] = f"Ficha N° {num_ficha} cadastrada com sucesso!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir dados no banco: {e}")
    else:
        st.warning("Preencha obrigatoriamente os campos 'Paciente' e 'Médico'.")

# --- ATUALIZAR ---
if submit_atualizar:
    if id_ativo:
        try:
            supabase.table("fichas").update(payload).eq("ficha", id_ativo).execute()
            st.session_state["mensagem_sucesso"] = "Ficha atualizada com sucesso!"
            limpar_campos_e_selecao()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar ficha: {e}")
    else:
        st.warning("Selecione uma ficha na tabela antes de tentar atualizar.")

# --- DELETAR ---
if submit_deletar:
    if id_ativo:
        dialog_confirmar_deletar(id_ativo)
    else:
        st.warning("Selecione uma ficha na tabela antes de tentar deletar.")

# --- LIMPAR ---
if submit_limpar:
    limpar_campos_e_selecao()
    st.rerun()