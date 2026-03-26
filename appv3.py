import streamlit as st
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
import re
from difflib import get_close_matches

st.set_page_config(layout="wide")

st.title("🧾 Leitor Inteligente de Cupons Fiscais (IA + Autocorrect)")

uploaded_files = st.file_uploader(
    "📎 Envie um ou mais cupons fiscais",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("👆 Selecione um ou mais arquivos para começar")

reader = easyocr.Reader(['pt','en'], gpu=False)

# 🚫 Palavras a ignorar
palavras_ignorar = [
    "CNPJ","CPF","SUBTOTAL","TOTAL","TROCO",
    "DATA","HORA","ENDERECO","ENDEREÇO"
]

# 🧠 Base de produtos conhecidos
base_produtos = [
    "PAO FORMA SEVEN BOYS",
    "CHA ERVA DOCE LEAO",
    "CARNE MOIDA PATINHO",
    "DETERGENTE LIQUIDO",
    "MOLHO DE TOMATE",
    "FARINHA DE TRIGO",
    "AGUA DE COCO",
    "REFRESCO EM PO TANG",
]

# 🔧 Correções diretas
correcoes_produtos = {
    "F0RNA": "FORMA",
    "FORNA": "FORMA",
    "BOVYS": "BOYS",
    "LEA0": "LEAO",
    "D0CE": "DOCE",
    "PAT1NHO": "PATINHO",
    "M01DA": "MOIDA",
    "TR1G0": "TRIGO",
    "F0MATE": "TOMATE",
    "L1Q": "LIQ",
    "C0C0": "COCO",
    "REFRE5": "REFRES",
}

# 🔥 Reconstruir linhas
def reconstruir_linhas(ocr_result):
    linhas = []
    for (bbox, texto, conf) in ocr_result:
        y = int(bbox[0][1])
        linhas.append((y, texto))

    linhas.sort(key=lambda x: x[0])

    linhas_agrupadas = []
    linha_atual = []
    y_atual = None

    for y, texto in linhas:
        if y_atual is None:
            y_atual = y

        if abs(y - y_atual) < 15:
            linha_atual.append(texto)
        else:
            linhas_agrupadas.append(" ".join(linha_atual))
            linha_atual = [texto]
            y_atual = y

    if linha_atual:
        linhas_agrupadas.append(" ".join(linha_atual))

    return linhas_agrupadas

# 🔥 Detectar bloco de itens
def filtrar_bloco_itens(linhas):
    bloco = []
    capturando = False
    contador = 0

    for linha in linhas:

        tem_preco = re.search(r'\d+[.,]\d{2}', linha)

        if tem_preco:
            contador += 1
        else:
            contador = 0

        if contador >= 2:
            capturando = True

        if any(p in linha for p in ["TOTAL", "TROCO", "SUBTOTAL"]):
            break

        if capturando:
            bloco.append(linha)

    return bloco

# 🧹 Limpeza
def limpar_ruido(texto):
    texto = re.sub(r'[^A-Z0-9\s.,()xX]', '', texto)
    texto = re.sub(r'(.)\1{3,}', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

# 🔄 Normalização
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

# 🧠 Correção direta
def corrigir_produto(nome):
    for erro, correto in correcoes_produtos.items():
        nome = re.sub(rf'\b{erro}\b', correto, nome)
    return nome

# 🧠 Correção fuzzy
def corrigir_fuzzy(nome):
    match = get_close_matches(nome, base_produtos, n=1, cutoff=0.6)
    return match[0] if match else nome

# 🧠 Pipeline final
def corrigir_nome_final(nome):
    nome = corrigir_produto(nome)
    nome = corrigir_fuzzy(nome)
    return nome

# 🎯 Validação
def linha_valida(linha):
    tem_preco = re.search(r'\d+[.,]\d{2}', linha)
    tem_texto = len(re.findall(r'[A-Z]', linha)) > 5
    return tem_preco and tem_texto

# 📦 Extrair item
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

# 🚀 PROCESSAMENTO
if uploaded_files:

    resultados = []

    st.subheader(f"📄 {len(uploaded_files)} cupom(ns) enviado(s)")

    for arquivo in uploaded_files:

        st.markdown(f"### 📌 {arquivo.name}")

        image = Image.open(arquivo)
        st.image(image, width=250)

        img = np.array(image)

        ocr_result = reader.readtext(img, detail=1, paragraph=False)

        linhas = reconstruir_linhas(ocr_result)
        linhas = [l.upper() for l in linhas]

        linhas_itens = filtrar_bloco_itens(linhas)

        for texto in linhas_itens:

            texto = limpar_ruido(texto)
            texto = normalizar_texto(texto)

            if any(p in texto for p in palavras_ignorar):
                continue

            if not linha_valida(texto):
                continue

            item = extrair_item(texto)

            if item:
                nome, qtd, preco = item

                nome = corrigir_nome_final(nome)

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

        total = df["preco"].sum()
        st.success(f"💰 Total geral: R$ {total:.2f}")

        df.to_excel("cupons.xlsx", index=False)
        df.to_csv("cupons.csv", index=False)

        with open("cupons.xlsx","rb") as f:
            st.download_button("📥 Excel", f, "cupons.xlsx")

        with open("cupons.csv","rb") as f:
            st.download_button("📥 CSV", f, "cupons.csv")

    else:
        st.warning("Nenhum item identificado")