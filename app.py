from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import io
import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# CONFIGURAÇÕES
# --------------------------------------------------

ARQUIVO_CREDENCIAIS = "streamlit-drive-8397492-ad479ef3cfe2.json"

# ID do arquivo Excel no Google Drive
FILE_ID = "1XLKIZqlpB8v4M0LRMbDUnn7d4IPAKN2P"



# --------------------------------------------------
# AUTENTICAÇÃO
# --------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]
@st.cache_data(ttl=300)
def carregar_planilha():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    drive = build(
        "drive",
        "v3",
        credentials=credentials
    )


# --------------------------------------------------
# BAIXAR O EXCEL
# --------------------------------------------------

    request = drive.files().get_media(
        fileId=FILE_ID
    )

    arquivo = io.BytesIO()

    downloader = MediaIoBaseDownload(
        arquivo,
        request
    )

    done = False

    while not done:
        status, done = downloader.next_chunk()

        if status:
            print(f"Download: {int(status.progress() * 100)}%")


# --------------------------------------------------
# LER COM PANDAS
# --------------------------------------------------

    arquivo.seek(0)

    df = pd.read_excel(arquivo, sheet_name="Relatório_2025", header=8)

    return df

df= carregar_planilha()

df.loc[df['SEMANA'] == 53, "SEMANA"] = 1

# -------------------------
# INTERFACE
# -------------------------

st.set_page_config(
    page_title="Análise Comercial",
    layout="wide"
)

st.title("Análise Comercial")

st.write(f"Quantidade de Contêiners: {len(df["Contêiner"].unique())}")


# -------------------------
# FILTRO
# -------------------------

clientes = st.multiselect(
    "Cliente",
    options=df["CLIENTE"].dropna().unique()
)

if clientes:
    df = df[df["CLIENTE"].isin(clientes)]


# -------------------------
# GRÁFICO
# -------------------------

media = (
    df.groupby(["SEMANA", "CLIENTE"])["Resultado por caixa"]
      .mean()
      .reset_index()
)

media = media.dropna()


fig = px.line(
    media,
    x="SEMANA",
    y="Resultado por caixa",
    color="CLIENTE",
    markers=True,
    title="Valor Medio por cliente"
)
st.plotly_chart(
    fig,
    width="stretch",
    height=600
)
