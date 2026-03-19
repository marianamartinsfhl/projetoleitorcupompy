import streamlit as st
import pytesseract
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import re
import os

# Caminho Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

st.title("🧾 Leitor Inteligente de Cupom Fiscal v3")

uploaded_file = st.file_uploader("Envie a imagem do cupom", type=["jpg","jpeg","png"])

palavras_ignorar = [
"CNPJ","CPF","SUBTOTAL","TOTAL","TROCO",
"DATA","HORA","ENDERECO","ENDEREÇO","ITEM"
]

def corrigir_ocr(texto):

    texto = texto.replace("0","O")
    texto = texto.replace("1","I")
    texto = texto.replace("5","S")
    texto = texto.replace("8","B")
    texto = texto.replace("4","A")

    return texto


def extrair_item(linha):

    linha = corrigir_ocr(linha)

    # detectar preço
    preco = re.findall(r'\d+[.,]\d{2}', linha)

    if not preco:
        return None

    preco = preco[-1]
    preco = preco.replace(",", ".")

    # detectar quantidade
    qtd = re.search(r'(\d+)\s*[xX]', linha)

    if qtd:
        quantidade = int(qtd.group(1))
    else:
        quantidade = 1

    # remover números do início
    nome = re.sub(r'^\d+\s+', '', linha)

    # remover preço
    nome = nome.replace(preco, "")

    # remover qtd
    nome = re.sub(r'\d+\s*[xX]', '', nome)

    # limpar
    nome = re.sub(r'\d{5,}', '', nome)
    nome = re.sub(r'\s+', ' ', nome)

    nome = nome.strip()

    if len(nome) < 4:
        return None

    return nome, quantidade, float(preco)


if uploaded_file is not None:

    image = Image.open(uploaded_file)
    st.image(image, caption="Cupom enviado", use_container_width=True)

    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)

    blur = cv2.GaussianBlur(gray,(3,3),0)

    _,thresh = cv2.threshold(blur,150,255,cv2.THRESH_BINARY)

    config = "--oem 3 --psm 6"

    texto = pytesseract.image_to_string(thresh, lang="por", config=config)

    st.subheader("Texto detectado")
    st.text(texto)

    linhas = [l.strip() for l in texto.split("\n") if l.strip()]

    produtos = []

    for linha in linhas:

        linha_upper = linha.upper()

        if any(p in linha_upper for p in palavras_ignorar):
            continue

        item = extrair_item(linha)

        if item:
            produtos.append(item)

    if produtos:

        df = pd.DataFrame(produtos, columns=["Produto","Quantidade","Preco"])

        st.subheader("🛒 Itens encontrados")

        st.dataframe(df)

        arquivo = "cupom_processado.xlsx"

        df.to_excel(arquivo,index=False)

        with open(arquivo,"rb") as f:
            st.download_button(
                "📥 Baixar Excel",
                data=f,
                file_name=arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:

        st.warning("Nenhum item identificado")