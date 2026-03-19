# 🧾 Leitor Inteligente de Cupom Fiscal com OCR

Projeto em **Python** que utiliza **OCR (Reconhecimento Óptico de Caracteres)** para extrair automaticamente itens de cupons fiscais a partir de imagens.

O sistema identifica produtos, quantidade e preço, gerando um **dataset estruturado** que pode ser utilizado para análise de dados ou integração com ferramentas como **Power BI**.

---

# 🚀 Funcionalidades

* Upload de **um ou vários cupons fiscais**
* Extração automática de:

  * Produto
  * Quantidade
  * Preço
* Detecção automática de **linhas do cupom usando OpenCV**
* OCR otimizado para cupons fiscais
* Exportação dos dados em:

  * Excel
  * CSV
* Dataset pronto para análise no **Power BI**

---

# 🧠 Tecnologias Utilizadas

* **Python**
* **OpenCV** – processamento de imagem
* **Tesseract OCR** – leitura de texto
* **Streamlit** – interface da aplicação
* **Pandas** – estruturação dos dados

---

# 📂 Estrutura do Projeto

```
leitor-cupom-ocr
│
├── app.py
├── requirements.txt
├── README.md
└── exemplos_cupons
```

---

# ⚙️ Instalação

Clone o repositório:

```
git clone https://github.com/marianamartinsfhl/projeto-leitor-cupom-py.git
```

Entre na pasta do projeto:

```
cd leitor-cupom-ocr
```

Instale as dependências:

```
pip install -r requirements.txt
```

---

# ▶️ Como Executar

Execute o aplicativo com:

```
py -m streamlit run app.py
```

O navegador abrirá automaticamente com a interface do sistema.

---

# 📊 Exemplo de Saída

| arquivo    | produto        | quantidade | preco |
| ---------- | -------------- | ---------- | ----- |
| cupom1.jpg | ARROZ TIO JOAO | 1          | 22.90 |
| cupom1.jpg | LEITE INTEGRAL | 2          | 5.49  |
| cupom2.jpg | FRANGO FILE    | 1          | 18.70 |

---

# 📈 Possíveis Aplicações

* Controle automático de gastos
* Digitalização de cupons fiscais
* Construção de datasets de consumo
* Integração com dashboards de BI
* Automação de entrada de dados fiscais

---

# 🔮 Melhorias Futuras

* Suporte para **PDF de notas fiscais**
* Integração direta com **Power BI**
* OCR com **modelos de IA mais avançados**
* Processamento em lote de grandes volumes de cupons

---

# 👩‍💻 Autora

Projeto desenvolvido por **Mariana Martins**
Profissional com ênfase em **dados, automação e BI**.
