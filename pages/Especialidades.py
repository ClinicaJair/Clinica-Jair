import streamlit as st
from st_supabase_connection import SupabaseConnection
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
supabase = st.connection("supabase", type=SupabaseConnection)

st.set_page_config(page_title="Cadastro de Especialidades", layout="wide")
st.title("Cadastro de Especialidades")

# 3. Inicialização do Session State para guardar o ID selecionado e limpar campos
if 'especialidade_selecionado_id' not in st.session_state:
    st.session_state.especialidade_selecionado_id = None
if 'update_trigger' not in st.session_state:
    st.session_state.update_trigger = 0

def limpar_campos():
    st.session_state.especialidade_selecionado_id = None
    st.session_state.update_trigger += 1

# Função auxiliar para ler os dados do Supabase
def carregar_dados():
    response = supabase.table("especialidades").select("*").execute()
    return pd.DataFrame(response.data)

# 3. Formulário de Cadastro e Edição (Create, Update, Delete)
#st.sidebar.header("Cadastro / Edição")
st.form("Cadastro / Edição")

df_dados = carregar_dados()
especialidade_selecionado = None

# Se um item do Dataframe for clicado, preenche o formulário
if 'selected_rows' in st.session_state and len(st.session_state.selected_rows['selection']['rows']) > 0:
    idx = st.session_state.selected_rows['selection']['rows'][0]
    especialidade_selecionado = df_dados.iloc[idx]
    st.session_state.especialidade_selecionado_id = especialidade_selecionado['codigo']

# Campos do formulário
#with st.sidebar.form(key=f"form_cliente_{st.session_state.update_trigger}"):
with st.form(key=f"form_especialidade_{st.session_state.update_trigger}"):
    #nome = st.text_input("Nome", value=especialidade_selecionado['nome'] if especialidade_selecionado is not None else "")
    #email = st.text_input("Email", value=especialidade_selecionado['email'] if especialidade_selecionado is not None else "")
    #telefone = st.text_input("Telefone", value=especialidade_selecionado['telefone'] if especialidade_selecionado is not None else "")

    # 1. Definir proporções (ex: 20% / 80%)
    col1, col2, = st.columns([1,6])

    # 2. Usar 'with' para adicionar widgets nas colunas
    with col1:
        #codigo = st.text_input("Codigo")
        codigo = st.text_input("Codigo", value=especialidade_selecionado['codigo'] if especialidade_selecionado is not None else "")

    with col2:
        #razao = st.text_input("Razão Social")
        nome = st.text_input("Nome da especialidade", value=especialidade_selecionado['nome'] if especialidade_selecionado is not None else "")



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
            data = supabase.table("especialidades").insert({"codigo": codigo, "nome": nome}).execute()
            st.success("especialidade cadastrado com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Preencha pelo menos a Nome.")

if submit_atualizar and st.session_state.especialidade_selecionado_id and nome:
    #data = supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id",
    #                                                                                                  st.session_state.especialidade_selecionado_id).execute()
    if codigo:
        try:
            supabase.table("especialidades").update({"codigo": codigo, "nome": nome,}).eq("codigo", st.session_state.especialidade_selecionado_id).execute()

            st.success("especialidade atualizado com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Selecione um especialidade para atualizar.")

if submit_deletar and st.session_state.especialidade_selecionado_id:
    #data = supabase.table("clientes").delete().eq("id", st.session_state.especialidade_selecionado_id).execute()
    if codigo:
        try:
            supabase.table("especialidades").delete().eq("codigo", st.session_state.especialidade_selecionado_id).execute()
            st.success("especialidade deletada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Selecione uma especialidade para deletar.")

if submit_limpar and st.session_state.especialidade_selecionado_id:
    #data = supabase.table("clientes").delete().eq("id", st.session_state.especialidade_selecionado_id).execute()
    if codigo:
        try:
            #supabase.table("especialidades").delete().eq("codigo", st.session_state.especialidade_selecionado_id).execute()
            #st.success("especialidade deletada com sucesso!")
            limpar_campos()
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    #else:
    #    st.warning("Selecione uma especialidade para deletar.")


# 4. Read (Exibição no Dataframe)3

st.subheader("Lista de especialidades Cadastrados")

if not df_dados.empty:
    filtro = st.text_input("Filtrar por Nome:")
    campos_tabela = ['nome']
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
        file_name='relatorio_especialidades.csv',
        mime='text/csv',
    )

    # Botão para download em PDF
    col_pdf.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_data,
        file_name='relatorio_especialidades.pdf',
        mime='application/pdf',
    )
else:
    st.info("Nenhum especialidade cadastrado.")

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
