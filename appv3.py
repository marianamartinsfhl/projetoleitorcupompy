import streamlit as st
import easyocr
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import re

st.title("🧾 Leitor Inteligente de Cupons v5 (IA)")

uploaded_files = st.file_uploader(
    "📎 Envie um ou mais cupons fiscais",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("👆 Selecione um ou mais arquivos para começar")

reader = easyocr.Reader(['pt','en'], gpu=False)

palavras_ignorar = [
"CNPJ","CPF","SUBTOTAL","TOTAL","TROCO",
"DATA","HORA","ENDERECO","ENDEREÇO"
]

def limpar_ruido(texto):
    texto = re.sub(r'[^\w\s.,()xX]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def normalizar_texto(texto):
    mapa = {"0":"O","1":"I","5":"S","8":"B"}
    palavras = texto.split()
    resultado = []

    for p in palavras:
        if not re.search(r'\d+[.,]\d{2}', p):
            for k,v in mapa.items():
                p = p.replace(k,v)
        resultado.append(p)

    return " ".join(resultado)

def linha_valida(linha):
    return (
        re.search(r'\d+[.,]\d{2}', linha) and
        re.search(r'[A-Z]{3,}', linha)
    )

def extrair_item(texto):

    precos = re.findall(r'\d+[.,]\d{2}', texto)

    if not precos:
        return None

    preco = float(precos[-1].replace(",", "."))

    qtd = re.search(r'(\d+)\s*[xX]', texto)
    quantidade = int(qtd.group(1)) if qtd else 1

    nome = texto

    nome = re.sub(r'^\d+\s+', '', nome)
    nome = nome.replace(precos[-1], "")
    nome = re.sub(r'\d+\s*[xX]', '', nome)
    nome = re.sub(r'\d{5,}', '', nome)
    nome = re.sub(r'\s+', ' ', nome)

    nome = nome.strip()

    if len(nome) < 3:
        return None

    return nome, quantidade, preco


if uploaded_files:

    resultados = []

    st.subheader(f"📄 {len(uploaded_files)} cupom(ns) enviado(s)")

    for arquivo in uploaded_files:

        st.markdown(f"### 📌 Processando: {arquivo.name}")

        image = Image.open(arquivo)
        st.image(image, width=250)

        img = np.array(image)

        ocr_result = reader.readtext(img)

        for (_, texto, _) in ocr_result:

            texto = texto.upper()
            texto = limpar_ruido(texto)
            texto = normalizar_texto(texto)

            if any(p in texto for p in palavras_ignorar):
                continue

            if not linha_valida(texto):
                continue

            item = extrair_item(texto)

            if item:
                nome, qtd, preco = item

                resultados.append({
                    "arquivo": arquivo.name,
                    "produto": nome,
                    "quantidade": qtd,
                    "preco": preco
                })
                
    if resultados:

        df = pd.DataFrame(resultados)

        st.subheader("🛒 Itens encontrados")
        st.dataframe(df)

        df.to_excel("cupons.xlsx", index=False)
        df.to_csv("cupons.csv", index=False)

        with open("cupons.xlsx","rb") as f:
            st.download_button("📥 Excel", f, "cupons.xlsx")

        with open("cupons.csv","rb") as f:
            st.download_button("📥 CSV", f, "cupons.csv")

        st.success("Dataset pronto para Power BI 🚀")

    else:
        st.warning("Nenhum item identificado")