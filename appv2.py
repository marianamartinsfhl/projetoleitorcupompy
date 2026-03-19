import streamlit as st
import pytesseract
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import re
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("🧾 Leitor Inteligente de Cupons v4")

uploaded_files = st.file_uploader(
    "Envie um ou vários cupons",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

palavras_ignorar = [
"CNPJ","CPF","SUBTOTAL","TOTAL","TROCO",
"DATA","HORA","ENDERECO","ENDEREÇO"
]


def detectar_linhas(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(5,5),0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        3
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(40,3))

    dilate = cv2.dilate(thresh,kernel,iterations=1)

    contornos,_ = cv2.findContours(
        dilate,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    linhas = []

    for c in contornos:

        x,y,w,h = cv2.boundingRect(c)

        if w > 200 and h < 80:
            linha = img[y:y+h,x:x+w]
            linhas.append((y,linha))

    linhas = sorted(linhas,key=lambda x:x[0])

    return [l[1] for l in linhas]


def extrair_item(texto):

    texto = texto.strip()

    preco = re.findall(r'\d+[.,]\d{2}',texto)

    if not preco:
        return None

    preco = preco[-1].replace(",", ".")

    qtd = re.search(r'(\d+)\s*[xX]',texto)

    if qtd:
        qtd = int(qtd.group(1))
    else:
        qtd = 1

    nome = re.sub(r'^\d+\s+','',texto)

    nome = nome.replace(preco,'')

    nome = re.sub(r'\d+\s*[xX]','',nome)

    nome = re.sub(r'\d{5,}','',nome)

    nome = re.sub(r'\s+',' ',nome)

    nome = nome.strip()

    if len(nome) < 3:
        return None

    return nome,qtd,float(preco)


if uploaded_files:

    resultados = []

    for arquivo in uploaded_files:

        image = Image.open(arquivo)

        img = np.array(image)

        linhas = detectar_linhas(img)

        for linha_img in linhas:

            config = "--oem 3 --psm 7"

            texto = pytesseract.image_to_string(
                linha_img,
                lang="por",
                config=config
            )

            texto_upper = texto.upper()

            if any(p in texto_upper for p in palavras_ignorar):
                continue

            item = extrair_item(texto)

            if item:

                nome,qtd,preco = item

                resultados.append({
                    "arquivo":arquivo.name,
                    "produto":nome,
                    "quantidade":qtd,
                    "preco":preco
                })

    if resultados:

        df = pd.DataFrame(resultados)

        st.subheader("🛒 Itens encontrados")

        st.dataframe(df)

        excel_file = "cupons_processados.xlsx"
        csv_file = "cupons_processados.csv"

        df.to_excel(excel_file,index=False)
        df.to_csv(csv_file,index=False)

        with open(excel_file,"rb") as f:
            st.download_button(
                "📥 Baixar Excel",
                f,
                excel_file
            )

        with open(csv_file,"rb") as f:
            st.download_button(
                "📥 Baixar CSV",
                f,
                csv_file
            )

        st.success("Dataset pronto para Power BI")

    else:

        st.warning("Nenhum item encontrado")