import streamlit as st
from st_supabase_connection import SupabaseConnection
from supabase import create_client
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

# 2. CSS para remover o espaçamento do topo
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

# 1. Conexão com o Banco de Dados (Substitua pelas suas credenciais do Supabase)
#supabase = st.connection("supabase", type=SupabaseConnection)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Cadastro de Pacientes", layout="wide")
st.title("Cadastro de Pacientes")

# 3. Inicialização do Session State para guardar o ID selecionado e limpar campos
if 'paciente_selecionado_id' not in st.session_state:
    st.session_state.paciente_selecionado_id = None
if 'update_trigger' not in st.session_state:
    st.session_state.update_trigger = 0

def limpar_campos():
    st.session_state.paciente_selecionado_id = None
    st.session_state.update_trigger += 1

# Função auxiliar para ler os dados do Supabase
def carregar_dados():
    response = supabase.table("pacientes").select("*").execute()
    return pd.DataFrame(response.data)

# 3. Formulário de Cadastro e Edição (Create, Update, Delete)
#st.sidebar.header("Cadastro / Edição")
st.form("Cadastro / Edição")

df_dados = carregar_dados()
paciente_selecionado = None

# Se um item do Dataframe for clicado, preenche o formulário
if 'selected_rows' in st.session_state and len(st.session_state.selected_rows['selection']['rows']) > 0:
    idx = st.session_state.selected_rows['selection']['rows'][0]
    paciente_selecionado = df_dados.iloc[idx]
    st.session_state.paciente_selecionado_id = paciente_selecionado['codigo']

# Campos do formulário
#with st.sidebar.form(key=f"form_cliente_{st.session_state.update_trigger}"):
with st.form(key=f"form_paciente_{st.session_state.update_trigger}"):
    #nome = st.text_input("Nome", value=paciente_selecionado['nome'] if paciente_selecionado is not None else "")
    #email = st.text_input("Email", value=paciente_selecionado['email'] if paciente_selecionado is not None else "")
    #telefone = st.text_input("Telefone", value=paciente_selecionado['telefone'] if paciente_selecionado is not None else "")

    # 1. Definir proporções (ex: 20% / 80%)
    col1, col2, col3, col4 = st.columns([1,6,4,2])
    col5, col6, col7, col8 = st.columns([3,3,2,7])
    col9, col10, col11, col12, col13 = st.columns([3,3,1,2,2])
    col14, col15, col16 = st.columns([3,3,3])

    # 2. Usar 'with' para adicionar widgets nas colunas
    with col1:
        #codigo = st.text_input("Codigo")
        codigo = st.text_input("Codigo", value=paciente_selecionado['codigo'] if paciente_selecionado is not None else "")

    with col2:
        #razao = st.text_input("Razão Social")
        nome = st.text_input("Nome do Paciente", value=paciente_selecionado['nome'] if paciente_selecionado is not None else "")

    with col3:
        #fantasia = st.text_input("Nome Fantasia")
        apelido = st.text_input("Apelido", value=paciente_selecionado['apelido'] if paciente_selecionado is not None else "")

    with col4:
        #data_fundacao = st.text_input("Data de Fundação")
        data_nascimento = st.text_input("Data de Nascimento", value=paciente_selecionado['data_nascimento'] if paciente_selecionado is not None else "")

    with col5:
        #cnpj = st.text_input("CNPJ")
        cpf = st.text_input("CPF", value=paciente_selecionado['cpf'] if paciente_selecionado is not None else "")

    with col6:
        #inscricao = st.text_input("Inscrição Estadual")
        rg = st.text_input("RG", value=paciente_selecionado['rg'] if paciente_selecionado is not None else "")

    with col7:
        #cep = st.text_input("CEP")
        cep = st.text_input("CEP", value=paciente_selecionado['cep'] if paciente_selecionado is not None else "")

    with col8:
        #endereco = st.text_input("Endereço")
        endereco = st.text_input("Endereço", value=paciente_selecionado['endereco'] if paciente_selecionado is not None else "")

    with col9:
        #bairro = st.text_input("Bairro")
        bairro = st.text_input("Bairro", value=paciente_selecionado['bairro'] if paciente_selecionado is not None else "")

    with col10:
        #cidade = st.text_input("Cidade")
        cidade = st.text_input("Cidade", value=paciente_selecionado['cidade'] if paciente_selecionado is not None else "")

    with col11:
        #estado = st.text_input("Estado")
        estado = st.text_input("Estado", value=paciente_selecionado['estado'] if paciente_selecionado is not None else "")

    with col12:
        #telefone = st.text_input("Telefone")
        telefone = st.text_input("Telefone", value=paciente_selecionado['telefone'] if paciente_selecionado is not None else "")

    with col13:
        #telefone1 = st.text_input("Telefone1")
        telefone1 = st.text_input("Telefone1", value=paciente_selecionado['telefone'] if paciente_selecionado is not None else "")

    with col14:
        #email = st.text_input("E-mail")
        contato = st.text_input("Contato", value=paciente_selecionado['contato'] if paciente_selecionado is not None else "")

    with col15:
        #site = st.text_input("Site")
        email = st.text_input("E-mail", value=paciente_selecionado['email'] if paciente_selecionado is not None else "")

    with col16:
        #instagram = st.text_input("Instagram")
        profissao = st.text_input("Profissão", value=paciente_selecionado['profissao'] if paciente_selecionado is not None else "")

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
if submit_criar and nome:
    if nome:
        try:
            #data = supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
            data = supabase.table("pacientes").insert({"codigo": codigo, "nome": nome, "apelido": apelido, "endereco": endereco,
                                                        "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado,
                                                        "telefone": telefone,
                                                        "telefone1": telefone1, "cpf": cpf, "rg": rg,
                                                        "data_nascimento": data_nascimento, "email": email, "contato": contato,
                                                        "profissao": profissao}).execute()
            st.success("Paciente cadastrado com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Preencha pelo menos a Nome.")

if submit_atualizar and st.session_state.paciente_selecionado_id and nome:
    #data = supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id",
    #                                                                                                  st.session_state.paciente_selecionado_id).execute()
    if codigo:
        try:
            supabase.table("pacientes").update({"codigo": codigo, "nome": nome, "apelido": apelido, "endereco": endereco,
                                                "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado,
                                                "telefone": telefone,
                                                "telefone1": telefone1, "cpf": cpf, "rg": rg,
                                                "data_nascimento": data_nascimento, "email": email, "contato": contato,
                                                "profissao": profissao}).eq("codigo", st.session_state.paciente_selecionado_id).execute()

            st.success("Paciente atualizado com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Selecione um Paciente para atualizar.")

if submit_deletar and st.session_state.paciente_selecionado_id:
    #data = supabase.table("clientes").delete().eq("id", st.session_state.paciente_selecionado_id).execute()
    if codigo:
        try:
            supabase.table("pacientes").delete().eq("codigo", st.session_state.paciente_selecionado_id).execute()
            st.success("Paciente deletada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Selecione uma Paciente para deletar.")

if submit_limpar and st.session_state.paciente_selecionado_id:
    #data = supabase.table("clientes").delete().eq("id", st.session_state.paciente_selecionado_id).execute()
    if codigo:
        try:
            #supabase.table("pacientes").delete().eq("codigo", st.session_state.paciente_selecionado_id).execute()
            #st.success("paciente deletada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    #else:
    #    st.warning("Selecione uma paciente para deletar.")


# 4. Read (Exibição no Dataframe)3

st.subheader("Lista de pacientes Cadastrados")

if not df_dados.empty:
    filtro = st.text_input("Filtrar por Nome:")
    campos_tabela = ['nome', 'apelido']
    if filtro:
        df_relatorio = df_dados[df_dados['nome'].str.contains(filtro, case=False, na=False)][campos_tabela]
    else:
        df_relatorio = df_dados[df_dados['nome'].str.contains('Null', case=False, na=False)][campos_tabela]

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
        file_name='relatorio_pacientes.csv',
        mime='text/csv',
    )

    # Botão para download em PDF
    col_pdf.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_data,
        file_name='relatorio_pacientes.pdf',
        mime='application/pdf',
    )
else:
    st.info("Nenhum Paciente cadastrado.")

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
