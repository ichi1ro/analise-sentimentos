# -----------------------------------------------------------
# 05_text_preprocess.py - Pré-processamento para Sentimento
# -----------------------------------------------------------

import re
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import json
import os

# ---- DOWNLOAD DOS RECURSOS NECESSÁRIOS ----
nltk.download('punkt')
nltk.download('punkt_tab')  # ← NECESSÁRIO para evitar erro!
nltk.download('stopwords')

# Carregar modelo de língua portuguesa para lematização
nlp = spacy.load("pt_core_news_sm")  # Instale com: python -m spacy download pt_core_news_sm

# Lista de stopwords
stop_words = set(stopwords.words('portuguese'))

# Função principal
def preprocessar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-zA-Zá-úÁ-Ú0-9 ]", " ", texto)
    tokens = word_tokenize(texto)
    tokens = [palavra for palavra in tokens if palavra not in stop_words]
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc]


# ----- LEITURA DO ARQUIVO DE NOTÍCIAS -----
input_path = "./pipeline_output/01_03/noticias_processadas_15.json"
output_path = "./pipeline_output/01_03/noticias_processadas_15_PROCESSADAS.json"

if not os.path.exists(input_path):
    raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

with open(input_path, "r", encoding="utf-8") as f:
    noticias = json.load(f)


# ----- PRÉ-PROCESSAMENTO -----
for noticia in noticias:
    conteudo = noticia.get("conteudo", "")
    noticia["conteudo_processado"] = preprocessar_texto(conteudo)


# ----- SALVAR -----
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(noticias, f, ensure_ascii=False, indent=2)

print(f"Processamento concluído! Arquivo salvo em: {output_path}")
