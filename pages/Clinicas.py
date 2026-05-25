import streamlit as st
from supabase import create_client
import pandas as pd

# Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
#url = "https://lcruodkgvahvyijbgbch.supabase.co"
#key = "sb_publishable_2dK9DdBevblDyz5ZhYtyaQ_6E0woJsZ"

supabase = create_client(url, key)

# 1. Configurar a página (opcional, mas recomendado)
st.set_page_config(layout="wide")

# 2. CSS para remover o espaçamento do topo
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

#******************
# 3. Funções do Banco de Dados (CRUD)
#def create_customer(nome, email, telefone):
#    supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
#    st.success("Cliente cadastrado com sucesso!")

#def read_customers():
#    response = supabase.table("clientes").select("*").execute()
#    return pd.DataFrame(response.data)

#def update_customer(cliente_id, nome, email, telefone):
#    supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id", cliente_id).execute()
#    st.success("Cliente atualizado com sucesso!")

#def delete_customer(cliente_id):
#    supabase.table("clientes").delete().eq("id", cliente_id).execute()
#    st.success("Cliente deletado com sucesso!")

#def obter_dados_tabela(clientes):
#    # Executa um SELECT * na tabela desejada
#    response = supabase.table(clientes).select("*").execute()
#    return response.data

def ler_clientes():
    response = supabase.table("clientes").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def cadastrar_cliente(nome, email, telefone):
    data = {"nome": nome, "email": email, "telefone": telefone}
    supabase.table("clientes").insert(data).execute()
    #st.success("Cliente cadastrado com sucesso!")

def atualizar_cliente(id_cliente, nome, email, telefone):
    data = {"nome": nome, "email": email, "telefone": telefone}
    supabase.table("clientes").update(data).eq("id", id_cliente).execute()
    #st.success("Cliente atualizado com sucesso!")

def deletar_cliente(id_cliente):
    supabase.table("clientes").delete().eq("id", id_cliente).execute()
    #st.success("Cliente deletado com sucesso!")

#******************

# 4. Layout da Interface (Formulário e DataFrame)
st.title("👤 Cadastro da Clinica")

with st.form("form_clinica"):

    st.write("Insira os dados abaixo:")

    # 1. Definir proporções (ex: 20% / 80%)
    col1, col2, col3, col4 = st.columns([1,6,4,2])
    col5, col6, col7, col8 = st.columns([3,3,2,7])
    col9, col10, col11, col12, col13 = st.columns([3,3,1,2,2])
    col14, col15, col16 = st.columns([3,3,3])

    # 2. Usar 'with' para adicionar widgets nas colunas
    with col1:
        codigo = st.text_input("Codigo")

    with col2:
        razao = st.text_input("Razão Social")

    with col3:
        fantasia = st.text_input("Nome Fantasia")

    with col4:
        data_fundacao = st.text_input("Data de Fundação")

    with col5:
        cnpj = st.text_input("CNPJ")

    with col6:
        inscricao = st.text_input("Inscrição Estadual")

    with col7:
        cep = st.text_input("CEP")

    with col8:
        endereco = st.text_input("Endereço")

    with col9:
        bairro = st.text_input("Bairro")

    with col10:
        cidade = st.text_input("Cidade")

    with col11:
        estado = st.text_input("Estado")

    with col12:
        telefone = st.text_input("Telefone")

    with col13:
        telefone1 = st.text_input("Telefone1")

    with col14:
        email = st.text_input("E-mail")

    with col15:
        site = st.text_input("Site")

    with col16:
        instagram = st.text_input("Instagram")

    st.write("")

    # 3. Coloca o botão de submit lado a lado com um botão de cancelar
    col_gravar, col_editar, col_deletar, col_cancelar = st.columns([2, 2, 2, 2])

    with col_gravar:
        # Botão de envio (Submit)
        #btn_create = st.form_submit_button("Cadastrar (Create)")
        #submit_gravar = st.form_submit_button(label='Salvar')
        btn_gravar = st.form_submit_button("➕ Gravar")

    with col_editar:
        # Botão de envio (Submit)
        #btn_create = st.form_submit_button("Cadastrar (Create)")
        #submit_gravar = st.form_submit_button(label='Salvar')
        btn_editar = st.form_submit_button("➕ Gravar1")

    with col_deletar:
        # Botão de envio (Submit)
        #btn_create = st.form_submit_button("Cadastrar (Create)")
        #submit_gravar = st.form_submit_button(label='Salvar')
        btn_deletar = st.form_submit_button("➕ Gravar2")

    with col_cancelar:
        # Botão de envio (Submit)
        #btn_create = st.form_submit_button("Cadastrar (Create)")
        #submit_gravar = st.form_submit_button(label='Salvar')
        btn_cancelar = st.form_submit_button("➕ Gravar3")

if btn_gravar:
    if razao:
        try:
            supabase.table("clinicas").insert({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
                                                "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado,
                                                "telefone": telefone,
                                                "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
                                                "data_fundacao": data_fundacao, "email": email, "site": site,
                                                "instagram": instagram}).execute()
            st.success(f"Clinica {razao} cadastrado!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Preencha pelo menos a Razão.")

if btn_editar:
    if st.button("✏️ Atualizar"):
        if codigo:
            try:
                supabase.table("clinicas").update({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
                                                    "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado,
                                                    "telefone": telefone,
                                                    "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
                                                    "data_fundacao": data_fundacao, "email": email, "site": site,
                                                    "instagram": instagram}).execute()
                st.success("Clinica atualizada!")
                #limpar_campos()
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
        else:
            st.warning("Selecione uma clinica para atualizar.")


if btn_deletar:
    # Botão comum (pode ser usado para cancelar/limpar)
    #submit_deletar = st.form_submit_button(label='Deletar')
    if st.button("🗑️ Deletar"):
        if codigo:
            try:
                supabase.table("clinicas").delete().eq("codigo", codigo).execute()
                st.success("Clinica deletada!")
                #limpar_campos()
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
        else:
            st.warning("Selecione uma clinica para deletar.")

if btn_cancelar:
    # Botão comum (pode ser usado para cancelar/limpar)
    #submit_cancelar = st.form_submit_button(label='Cancelar')
    if st.button("🧹 Limpar Campos"):
        #limpar_campos()
        st.success(f"Registro Cancelado!")
        st.rerun()

# Listar clientes
st.subheader("Clinicas Cadastrados")
response = supabase.table("clinicas").select("*").execute()
st.dataframe(response.data)

# Aba 2: Exibição dos dados e Seleção Interativa
#st.subheader("Lista de Clientes")
#df_clientes = get_clinicas()

#if not df_clientes.empty:
    # Seleção nativa de linhas do Streamlit (on_select="rerun" para atualizar a tela)
#    event = st.dataframe(
#        df_clientes,
#        use_container_width=True,
#        hide_index=True,
#        on_select="rerun",
#        selection_mode="single-row"
#    )

    # Ao clicar em uma linha, atualiza o session_state e recarrega a tela
#    if event.selection.rows:
#        selected_index = event.selection.rows[0]
#        st.session_state.selected_customer_id = df_clientes.iloc[selected_index]['id']
#else:
#    st.info("Nenhum cliente cadastrado ainda.")