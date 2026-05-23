import streamlit as st
from supabase import create_client

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
def create_customer(nome, email, telefone):
    supabase.table("clientes").insert({"nome": nome, "email": email, "telefone": telefone}).execute()
    st.success("Cliente cadastrado com sucesso!")

def read_customers():
    response = supabase.table("clientes").select("*").execute()
    return pd.DataFrame(response.data)

def update_customer(cliente_id, nome, email, telefone):
    supabase.table("clientes").update({"nome": nome, "email": email, "telefone": telefone}).eq("id", cliente_id).execute()
    st.success("Cliente atualizado com sucesso!")

def delete_customer(cliente_id):
    supabase.table("clientes").delete().eq("id", cliente_id).execute()
    st.success("Cliente deletado com sucesso!")

def obter_dados_tabela(clientes):
    # Executa um SELECT * na tabela desejada
    response = supabase.table(clientes).select("*").execute()
    return response.data

#******************

# 4. Layout da Interface (Formulário e DataFrame)
st.title("👤 Cadastro da Clinica")

with st.form("form_clinica"):

    #st.write("Insira os dados abaixo:")

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

    #st.divider()

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
        # 3. Interface do Streamlit
        #st.title("Exemplo de Combobox com Supabase")

        # Substitua 'sua_tabela' pelo nome da tabela real no seu banco de dados
        #tabela_selecionada = "clientes"

        # Busca os dados
        #dados = obter_dados_tabela(tabela_selecionada)

        #if dados:
            # Suponha que sua tabela tenha uma coluna chamada 'nome' que você quer exibir no combobox
            #opcoes = [linha["nome"] for linha in dados]

            # Cria a combobox (selectbox)
            #opcao_selecionada = st.selectbox("Seleciona uma opção da tabela:", opcoes)
            #opcao_selecionada = st.selectbox("", opcoes)

            # Exibe a escolha do usuário
            #st.write(f"Você selecionou: {opcao_selecionada}")
        #else:
            #st.warning("Nenhum dado encontrado ou erro na conexão.")

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

    # 3. Coloca o botão de submit lado a lado com um botão de cancelar
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])

    with col_btn1:
        # Botão de envio (Submit)
        submit = st.form_submit_button(label='Salvar')
    with col_btn2:
        # Botão comum (pode ser usado para cancelar/limpar)
        submit1 = st.form_submit_button(label='Deletar')
    with col_btn3:
        # Botão comum (pode ser usado para cancelar/limpar)
        submit2 = st.form_submit_button(label='Cancelar')


#    submit = st.form_submit_button("Cadastrar")
#    submit1 = st.form_submit_button("Deletart")
#    submit2 = st.form_submit_button("Sair")

if submit:
    # Inserir no PostgreSQL
    supabase.table("clinicas").insert({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
                                       "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado, "telefone": telefone,
                                       "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
                                       "data_fundacao": data_fundacao, "email": email, "site": site, "instagram": instagram}).execute()
    st.success(f"Clinica {razao} cadastrado!")
    clear_on_submit = True
    #st.rerun()

if submit1:
    # Deletar no PostgreSQL
    #supabase.table("clinicas").insert({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
    #                                   "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado, "telefone": telefone,
    #                                   "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
    #                                   "data_fundacao": data_fundacao, "email": email, "site": site, "instagram": instagram}).execute()
    supabase.table("clientes").delete().eq("codigo", clinicas['codigo']).execute()
    #st.success("Cliente excluído!")
    st.success(f"Clinica {razao} deletada!")
    clear_on_submit = True
    #st.rerun()

if submit2:
    # Cancelar no Cadastro
    #supabase.table("clinicas").insert({"codigo": codigo, "razao": razao, "fantasia": fantasia, "endereco": endereco,
    #                                   "cep": cep, "bairro": bairro, "cidade": cidade, "estado": estado, "telefone": telefone,
    #                                   "telefone1": telefone1, "cnpj": cnpj, "inscricao": inscricao,
    #                                   "data_fundacao": data_fundacao, "email": email, "site": site, "instagram": instagram}).execute()
    #st.success(f"Clinica {razao} cadastrado!")
    st.text_input[razao] = ''
    st.success(f"Registro Cancelado!")
    clear_on_submit = True
    #st.rerun()

# Listar clientes
#st.subheader("Clinicas Cadastrados")
#response = supabase.table("clinicas").select("*").execute()
#st.dataframe(response.data)

# Aba 2: Exibição dos dados e Seleção Interativa
st.subheader("Lista de Clientes")
#df_clientes = get_clinicas()

if not df_clientes.empty:
    # Seleção nativa de linhas do Streamlit (on_select="rerun" para atualizar a tela)
    event = st.dataframe(
        df_clientes,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Ao clicar em uma linha, atualiza o session_state e recarrega a tela
    if event.selection.rows:
        selected_index = event.selection.rows[0]
        st.session_state.selected_customer_id = df_clientes.iloc[selected_index]['id']
else:
    st.info("Nenhum cliente cadastrado ainda.")