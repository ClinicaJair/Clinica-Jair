import streamlit as st

st.set_page_config(page_title="Sistema Comercial", page_icon="📊", layout="wide")

st.title("🚀 Sistema Comercial Integrado")
st.markdown("---")

st.header("Bem-vindo ao Dashboard de Gestão")

col1, col2, col3 = st.columns(3)
col1.metric("Clientes", "150", "+5")
col2.metric("Produtos", "320", "12")
col3.metric("Vendas Mensais", "R$ 15.000", "+12%")

st.markdown("""
### Como utilizar
Use o menu lateral para navegar entre as telas de **Cadastro** e **Relatórios**.
- **Cadastro Clientes**: Adicionar ou editar clientes.
- **Cadastro Produtos**: Adicionar ou editar produtos.
- **Relatório Vendas**: Visualizar vendas consolidadas.
""")