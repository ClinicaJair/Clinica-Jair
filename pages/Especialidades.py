import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

# Configuração da Página
st.set_page_config(page_title="Sistema Comercial", layout="wide")
st.title("Gestão de Clientes")

# Conexão com o Supabase
supabase = st.connection("supabase_connection", type=SupabaseConnection)

# Abas para navegação
aba_cadastro, aba_relatorio = st.tabs(["Cadastrar Cliente", "Relatório de Clientes"])

# Aba 1: Cadastro
with aba_cadastro:
    st.subheader("Novo Cadastro")

    with st.form("form_cliente", clear_on_submit=True):
        codigo = st.number_input("Codigo")
        data_fundacao = st.date_input("Data")
        nome = st.text_input("Nome Completo")
        #documento = st.text_input("CPF ou CNPJ")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone")

        submitted = st.form_submit_button("Salvar Cliente")

        if submitted:
            if nome:
                # Inserindo dados no PostgreSQL via Supabase
                data = supabase.table("clinicas").insert(
                    {"codigo": codigo, "data_fundacao": data_fundacao, "nome": nome, "email": email, "telefone": telefone}
                ).execute()

                st.success(f"Cliente {nome} cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha pelo menos o nome do cliente.")

# Aba 2: Relatório
with aba_relatorio:
    st.subheader("Clientes Cadastrados")

    # Buscando os dados no banco
    response = supabase.table("clinicas").select("*").execute()

    if response.data:
        df_clientes = pd.DataFrame(response.data)

        # Exibição interativa com Streamlit
        st.dataframe(df_clientes, use_container_width=True)

        # Botão para download do relatório
        st.download_button(
            label="Exportar para CSV",
            data=df_clientes.to_csv(index=False).encode('utf-8'),
            file_name='relatorio_clientes.csv',
            mime='text/csv',
        )
    else:
        st.info("Nenhum cliente cadastrado ainda.")
