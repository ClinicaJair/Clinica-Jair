import streamlit as st
from supabase import create_client, Client
import pandas as pd
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

# 1. Conexão com o Banco de Dados (Substitua pelas suas credenciais do Supabase)
#supabase = st.connection("supabase", type=SupabaseConnection)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. CSS para remover o espaçamento do topo
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)


st.set_page_config(page_title="Cadastro de Clinicas", layout="wide")
st.title("Cadastro de Clinicas")

# 3. Inicialização do Session State para guardar o ID selecionado e limpar campos
if 'clinica_selecionado_id' not in st.session_state:
    st.session_state.clinica_selecionado_id = None
if 'update_trigger' not in st.session_state:
    st.session_state.update_trigger = 0

def limpar_campos():
    st.session_state.clinica_selecionado_id = None
    st.session_state.update_trigger += 1

# Função auxiliar para ler os dados do Supabase
def carregar_dados():
    response = supabase.table("clinicas").select("*").execute()
    return pd.DataFrame(response.data)

# 1. Função para buscar dados da tabela origem (ex: 'categorias')
def buscar_estado():
    response = supabase.table("estados").select("sigla, nome").execute()
    # Converte a resposta para um DataFrame do Pandas
    df = pd.DataFrame(response.data)
    return df

# 3. Formulário de Cadastro e Edição (Create, Update, Delete)
#st.sidebar.header("Cadastro / Edição")
st.form("Cadastro / Edição")

df_dados = carregar_dados()
clinica_selecionado = None

# Se um item do Dataframe for clicado, preenche o formulário
if 'selected_rows' in st.session_state and len(st.session_state.selected_rows['selection']['rows']) > 0:
    idx = st.session_state.selected_rows['selection']['rows'][0]
    clinica_selecionado = df_dados.iloc[idx]
    st.session_state.clinica_selecionado_id = clinica_selecionado['codigo']

# Campos do formulário
#with st.sidebar.form(key=f"form_cliente_{st.session_state.update_trigger}"):
with st.form(key=f"form_cliente_{st.session_state.update_trigger}"):
    #nome = st.text_input("Nome", value=clinica_selecionado['nome'] if clinica_selecionado is not None else "")
    #email = st.text_input("Email", value=clinica_selecionado['email'] if clinica_selecionado is not None else "")
    #telefone = st.text_input("Telefone", value=clinica_selecionado['telefone'] if clinica_selecionado is not None else "")

    # 1. Definir proporções (ex: 20% / 80%)
    col1, col2, col3, col4 = st.columns([1,6,4,2])
    col5, col6, col7, col8 = st.columns([3,3,2,7])
    col9, col10, col11, col12, col13 = st.columns([3,3,1,2,2])
    col14, col15, col16 = st.columns([3,3,3])

    # 2. Usar 'with' para adicionar widgets nas colunas
    with col1:
        #codigo = st.text_input("Codigo")
        codigo = st.text_input("Codigo", value=clinica_selecionado['codigo'] if clinica_selecionado is not None else "")

    with col2:
        #razao = st.text_input("Razão Social")
        razao = st.text_input("Razão Social", value=clinica_selecionado['razao'] if clinica_selecionado is not None else "")

    with col3:
        #fantasia = st.text_input("Nome Fantasia")
        fantasia = st.text_input("Nome Fantasia", value=clinica_selecionado['fantasia'] if clinica_selecionado is not None else "")

    with col4:
        #data_fundacao = st.text_input("Data de Fundação")
        data_fundacao = st.text_input("Data de Fundação", value=clinica_selecionado['data_fundacao'] if clinica_selecionado is not None else "")

    with col5:
        #cnpj = st.text_input("CNPJ")
        cnpj = st.text_input("CNPJ", value=clinica_selecionado['cnpj'] if clinica_selecionado is not None else "")

    with col6:
        #inscricao = st.text_input("Inscrição Estadual")
        inscricao = st.text_input("Inscrição Estadual", value=clinica_selecionado['inscricao'] if clinica_selecionado is not None else "")

    with col7:
        #cep = st.text_input("CEP")
        cep = st.text_input("CEP", value=clinica_selecionado['cep'] if clinica_selecionado is not None else "")

    with col8:
        #endereco = st.text_input("Endereço")
        endereco = st.text_input("Endereço", value=clinica_selecionado['endereco'] if clinica_selecionado is not None else "")

    with col9:
        #bairro = st.text_input("Bairro")
        bairro = st.text_input("Bairro", value=clinica_selecionado['bairro'] if clinica_selecionado is not None else "")

    with col10:
        #cidade = st.text_input("Cidade")
        cidade = st.text_input("Cidade", value=clinica_selecionado['cidade'] if clinica_selecionado is not None else "")

    with col11:
        #estado = st.text_input("Estado")
        #estado = st.text_input("Estado", value=clinica_selecionado['estado'] if clinica_selecionado is not None else "")
        # Busca os dados no Supabase para preencher o selectbox
        df_categorias = buscar_estado()
        opcoes_exibicao = df_categorias["sigla"].tolist()

        # Componente nativo do Streamlit
        estado = st.selectbox("Selecione uma categoria:", opcoes_exibicao)

        # Pega o ID correspondente à opção selecionada
        #id_selecionado = df_categorias.loc[df_categorias["nome_categoria"] == escolha_estado, "id"].iloc[0]
        #estado = st.text_input("Estado", value=escolha_estado if escolha_estado is not None else "")

    with col12:
        #telefone = st.text_input("Telefone")
        telefone = st.text_input("Telefone", value=clinica_selecionado['telefone'] if clinica_selecionado is not None else "")

    with col13:
        #telefone1 = st.text_input("Telefone1")
        telefone1 = st.text_input("Telefone1", value=clinica_selecionado['telefone'] if clinica_selecionado is not None else "")

    with col14:
        #email = st.text_input("E-mail")
        email = st.text_input("E-mail", value=clinica_selecionado['email'] if clinica_selecionado is not None else "")

    with col15:
        #site = st.text_input("Site")
        site = st.text_input("Site", value=clinica_selecionado['site'] if clinica_selecionado is not None else "")

    with col16:
        #instagram = st.text_input("Instagram")
        instagram = st.text_input("Instagram", value=clinica_selecionado['instagram'] if clinica_selecionado is not None else "")

    col17, col18, col19, col20 = st.columns(4)

    # Botão CREATE
    submit_criar = col17.form_submit_button("➕ Inserir")
    # Botão UPDATE
    submit_atualizar = col18.form_submit_button("✏️ Atualizar")
    # Botão DELETE
    submit_deletar = col19.form_submit_button("️🗑️ Deletar")
    # Botão LIMPAR
    submit_limpar = col20.form_submit_button("️🧹️ Limpar")

# Lógica dos botões
if submit_criar and razao:
    if razao:
        try:
            #data = supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
            data = supabase.table("clinicas").insert({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
                                                        "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado,
                                                        "telefone": telefone,
                                                        "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
                                                        "data_fundacao": data_fundacao, "email": email, "site": site,
                                                        "instagram": instagram}).execute()
            st.success("Clinica cadastrada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Preencha pelo menos a Razão Social.")

if submit_atualizar and st.session_state.clinica_selecionado_id and razao:
    #data = supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id",
    #                                                                                                  st.session_state.clinica_selecionado_id).execute()
    if codigo:
        try:
            supabase.table("clinicas").update({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
                                                "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado,
                                                "telefone": telefone,
                                                "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
                                                "data_fundacao": data_fundacao, "email": email, "site": site,
                                                "instagram": instagram}).eq("codigo", st.session_state.clinica_selecionado_id).execute()
            st.success("Clinica atualizada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Selecione uma clinica para atualizar.")

if submit_deletar and st.session_state.clinica_selecionado_id:
    #data = supabase.table("clientes").delete().eq("id", st.session_state.clinica_selecionado_id).execute()
    if codigo:
        try:
            supabase.table("clinicas").delete().eq("codigo", st.session_state.clinica_selecionado_id).execute()
            st.success("Clinica deletada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Selecione uma clinica para deletar.")

if submit_limpar and st.session_state.clinica_selecionado_id:
    #data = supabase.table("clientes").delete().eq("id", st.session_state.clinica_selecionado_id).execute()
    if codigo:
        try:
            #supabase.table("clinicas").delete().eq("codigo", st.session_state.clinica_selecionado_id).execute()
            #st.success("Clinica deletada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    #else:
    #    st.warning("Selecione uma clinica para deletar.")


# 4. Read (Exibição no Dataframe)
st.subheader("Lista de Clinicas Cadastrados")

if not df_dados.empty:
    filtro = st.text_input("Filtrar por Razão Social:")
    campos_tabela = ['razao', 'fantasia']
    df_dados = carregar_dados()
    if filtro:
        df_relatorio = df_dados[df_dados['razao'].str.contains(filtro, case=False, na=False)][campos_tabela]
    else:
        df_relatorio = df_dados[df_dados['razao'].str.contains('Null', case=False, na=False)][campos_tabela]

    # Seleção do dataframe (clicar no item seleciona ele)
    event = st.dataframe(
        df_relatorio,
        use_container_width=True,
        on_select="rerun",
       selection_mode="single-row",
        key="selected_rows"
    )
    #st.dataframe(df_relatorio, use_container_width=True)


    # Função para gerar PDF em memória
    def gerar_pdf(dataframe):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        data_table = [dataframe.columns.tolist()] + dataframe.values.tolist()

        t = Table(data_table)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


    pdf_data = gerar_pdf(df_relatorio)

    col_csv, col_pdf = st.columns(2)

    # Botão para download em CSV
    csv = df_relatorio.to_csv(index=False).encode('utf-8')
    col_csv.download_button(
        label="📄 Baixar Relatório em CSV",
        data=csv,
        file_name='relatorio_clientes.csv',
        mime='text/csv',
    )

    # Botão para download em PDF
    col_pdf.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_data,
        file_name='relatorio_clientes.pdf',
        mime='application/pdf',
    )
else:
    st.info("Nenhum cliente cadastrado.")

# 5. Relatório Interativo com Filtro e Impressão/Download
#st.subheader("Relatório e Exportação")

#if not df_dados.empty:
#    filtro = st.text_input("Filtrar por Razão Social:")
#    if filtro:
#        df_relatorio = df_dados[df_dados['razao'].str.contains(filtro, case=False, na=False)]
#    else:
#        df_relatorio = df_dados
#
#    st.dataframe(df_relatorio, use_container_width=True)
#
#
#    # Função para gerar PDF em memória
#    def gerar_pdf(dataframe):
#        buffer = io.BytesIO()
#        doc = SimpleDocTemplate(buffer, pagesize=letter)
#        elements = []
#
#        data_table = [dataframe.columns.tolist()] + dataframe.values.tolist()
#        t = Table(data_table)
#        t.setStyle(TableStyle([
#            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#            ('GRID', (0, 0), (-1, -1), 1, colors.black)
#        ]))
#        elements.append(t)
#        doc.build(elements)
#        buffer.seek(0)
#        return buffer.getvalue()
#
#
#    pdf_data = gerar_pdf(df_relatorio)
#
#    col_csv, col_pdf = st.columns(2)
#
#    # Botão para download em CSV
#    csv = df_relatorio.to_csv(index=False).encode('utf-8')
#    col_csv.download_button(
#        label="📄 Baixar Relatório em CSV",
#        data=csv,
#        file_name='relatorio_clientes.csv',
#        mime='text/csv',
#    )
#
#    # Botão para download em PDF
#    col_pdf.download_button(
#        label="📥 Baixar Relatório em PDF",
#        data=pdf_data,
#        file_name='relatorio_clientes.pdf',
#        mime='application/pdf',
#    )
