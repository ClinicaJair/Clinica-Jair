import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px

# 1. Conexão com o Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

st.set_page_config(page_title="Gestão de Metas 2026", layout="wide")
st.title("🚀 Sistema de Gestão de Metas e Processos")

# Opções de Navegação na Barra Lateral
menu = ["Dashboard & Relatórios", "Cadastrar Novo Processo", "Atualizar / Repactuar"]
choice = st.sidebar.selectbox("Navegação", menu)


# --- FUNÇÃO AUXILIAR PARA ATRIBUIR STATUS ---
def calcular_status(row):
    hoje = datetime.now().date()
    if pd.notna(row['data_conclusao']):
        # Converte para date se for timestamp do pandas
        dt_concl = pd.to_datetime(row['data_conclusao']).date()
        dt_orig = pd.to_datetime(row['prazo_original']).date()
        return "Concluído com Atraso" if dt_concl > dt_orig else "Concluído"
    else:
        dt_rev = pd.to_datetime(row['prazo_revisado']).date()
        if hoje > dt_rev:
            return "Atrasado"
        elif (dt_rev - hoje).days <= 3:
            return "Alerta (Prazo Próximo)"
        return "Em Andamento"


# --- ABA 1: DASHBOARD & RELATÓRIOS ---
if choice == "Dashboard & Relatórios":
    st.subheader("📊 Indicadores de Performance")

    # Buscar dados do banco
    response = supabase.table("processos").select("*, areas(nome)").execute()

    if response.data:
        df = pd.DataFrame(response.data)
        # Tratar o nome da área vindo do relacionamento
        df['area'] = df['areas'].apply(lambda x: x['nome'] if isinstance(x, dict) else 'Sem Área')
        df['status'] = df.apply(calcular_status, axis=1)

        # Mudar formato de datas
        df['prazo_original'] = pd.to_datetime(df['prazo_original']).dt.date
        df['prazo_revisado'] = pd.to_datetime(df['prazo_revisado']).dt.date

        # Cards Superiores
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total de Processos", len(df))
        kpi2.metric("Concluídos", len(df[df['status'].str.contains("Concluído")]))
        kpi3.metric("Em Andamento", len(df[df['status'] == "Em Andamento"]))
        kpi4.metric("Atrasados 🚨", len(df[df['status'] == "Atrasado"]))

        st.markdown("---")

        # Gráficos Dinâmicos
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Distribuição por Status")
            fig_status = px.pie(df, names='status', color='status',
                                color_discrete_map={
                                    "Concluído": "#10B981", "Concluído com Atraso": "#059669",
                                    "Em Andamento": "#3B82F6", "Alerta (Prazo Próximo)": "#F59E0B", "Atrasado": "#EF4444"
                                })
            st.plotly_chart(fig_status, use_container_width=True)

        with col2:
            st.markdown("### Processos por Área")
            fig_area = px.bar(df, x='area', color='status', barmode='stack', title="Status por Setor")
            st.plotly_chart(fig_area, use_container_width=True)

        st.markdown("### 📋 Visão Geral dos Processos")
        st.dataframe(df[['id', 'meta', 'responsavel', 'area', 'prazo_original', 'prazo_revisado', 'status', 'justificativa']],
                     use_container_width=True)
    else:
        st.info("Nenhum processo cadastrado no banco de dados até o momento.")

# --- ABA 2: CADASTRAR NOVO PROCESSO ---
elif choice == "Cadastrar Novo Processo":
    st.subheader("📝 Formulário de Cadastro")

    # Buscar áreas cadastradas para o Selectbox
    areas_resp = supabase.table("areas").select("*").execute()
    dict_areas = {item['nome']: item['id'] for item in areas_resp.data}

    with st.form("cadastro_form", clear_on_submit=True):
        meta = st.text_input("Nome da Meta / Entrega do Processo")
        responsavel = st.text_input("Nome do Responsável")
        area_selecionada = st.selectbox("Área / Setor", list(dict_areas.keys()))
        prazo_original = st.date_input("Prazo Original de Entrega")

        submetido = st.form_submit_button("Salvar no Banco de Dados")

        if submetido:
            if meta and responsavel:
                payload = {
                    "meta": meta,
                    "responsavel": responsavel,
                    "area_id": dict_areas[area_selecionada],
                    "prazo_original": str(prazo_original),
                    "prazo_revisado": str(prazo_original)  # Inicialmente são iguais
                }
                supabase.table("processos").insert(payload).execute()
                st.success(f"🎉 '{meta}' cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios.")

# --- ABA 3: ATUALIZAR / REPACTUAR ---
elif choice == "Atualizar / Repactuar":
    st.subheader("🔄 Gestão de Atrasos e Atualizações")

    res = supabase.table("processos").select("id, meta").execute()
    if res.data:
        dict_processos = {f"{item['id']} - {item['meta']}": item['id'] for item in res.data}
        proc_selecionado = st.selectbox("Escolha o processo para atualizar", list(dict_processos.keys()))
        id_atualizar = dict_processos[proc_selecionado]

        # Buscar dados atuais do item escolhido
        dados_atuais = supabase.table("processos").select("*").eq("id", id_atualizar).execute().data[0]

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Prazo Original:** {dados_atuais['prazo_original']}")
            nova_data_conclusao = st.date_input("Marcar Data de Conclusão (Se finalizado)", value=None)
        with col2:
            novo_prazo_revisado = st.date_input("Novo Prazo Revisado (Se houver alteração/atraso)",
                                                value=datetime.strptime(dados_atuais['prazo_revisado'], "%Y-%m-%d").date())
            justificativa = st.text_area("Justificativa da mudança (Obrigatório em caso de alteração de prazo)",
                                         value=dados_atuais['justificativa'] or "")

        if st.button("Gravar Atualizações"):
            update_payload = {
                "prazo_revisado": str(novo_prazo_revisado),
                "justificativa": justificativa
            }
            if nova_data_conclusao is not None:
                update_payload["data_conclusao"] = str(nova_data_conclusao)

            supabase.table("processos").update(update_payload).eq("id", id_atualizar).execute()
            st.success("Registro atualizado com sucesso na base de dados!")
            st.rerun()