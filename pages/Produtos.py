import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuração da sua conexão com o Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="CRUD de Clientes", layout="wide")
st.title("Cadastro de Clientes e Estados")


# --- FUNÇÕES AUXILIARES (READ) ---
def get_clientes():
    response = supabase.table("clientes").select("id, nome, estados(id, sigla, nome)").execute()
    # Tratando o retorno para facilitar a exibição
    dados = []
    for item in response.data:
        estado_info = item.get("estados") or {}
        dados.append({
            "ID": item["id"],
            "Nome": item["nome"],
            "Estado": estado_info.get("nome"),
            "estado_id": estado_info.get("id")
        })
    return pd.DataFrame(dados)


def get_estados():
    response = supabase.table("estados").select("id, nome").execute()
    return response.data


# --- TELA DE CADASTRO E EDIÇÃO ---
st.subheader("Gerenciar Clientes")

# Pegando os estados para o st.selectbox
estados_lista = get_estados()
estado_nomes = [est["nome"] for est in estados_lista]
estado_ids = {est["nome"]: est["id"] for est in estados_lista}

# Variáveis de controle para seleção
col1, col2 = st.columns([1, 1])

with col1:
    with st.form("form_cliente", clear_on_submit=True):
        nome_input = st.text_input("Nome do Cliente")
        estado_selecionado = st.selectbox("Estado", estado_nomes)

        submitted = st.form_submit_button("Cadastrar Cliente")
        if submitted and nome_input:
            estado_id = estado_ids[estado_selecionado]
            supabase.table("clientes").insert({"nome": nome_input, "estado_id": estado_id}).execute()
            st.success("Cliente cadastrado!")
            st.rerun()

with col2:
    st.subheader("Atualizar ou Excluir Cliente")
    # Carrega os dados atuais
    df_clientes = get_clientes()

    if not df_clientes.empty:
        # Exibindo os dados e permitindo clique/seleção
        event = st.dataframe(df_clientes[["ID", "Nome", "Estado"]], use_container_width=True, selection_mode="single-row",
                             on_select="rerun")
        selected_rows = event.selection.rows

        if selected_rows:
            index_selecionado = selected_rows[0]
            cliente_selecionado = df_clientes.iloc[index_selecionado]

            st.write(f"**Editando ID {cliente_selecionado['ID']}**")

            with st.form("form_update"):
                novo_nome = st.text_input("Novo Nome", value=cliente_selecionado["Nome"])
                novo_estado = st.selectbox("Novo Estado", estado_nomes, index=estado_nomes.index(cliente_selecionado["Estado"]))

                btn_update = st.form_submit_button("Atualizar")
                btn_delete = st.form_submit_button("Deletar")

                if btn_update:
                    estado_id_novo = estado_ids[novo_estado]
                    supabase.table("clientes").update({"nome": novo_nome, "estado_id": estado_id_novo}).eq("id", cliente_selecionado[
                        "ID"]).execute()
                    st.success("Registro atualizado!")
                    st.rerun()

                if btn_delete:
                    supabase.table("clientes").delete().eq("id", cliente_selecionado["ID"]).execute()
                    st.success("Registro deletado!")
                    st.rerun()
    else:
        st.info("Nenhum cliente cadastrado ainda.")
