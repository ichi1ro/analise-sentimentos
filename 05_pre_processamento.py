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
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('portuguese'))
except:
    # Fallback: lista manual de stopwords em português
    stop_words = set([
        'a', 'o', 'e', 'é', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as', 'dos', 'das',
        'para', 'com', 'no', 'na', 'que', 'por', 'se', 'ao', 'mais', 'como', 'mas', 'foi',
        'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há',
        'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela',
        'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me',
        'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas',
        'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual',
        'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse',
        'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus',
        'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes',
        'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo'
    ])

# Carregar modelo de língua portuguesa para lematização
nlp = spacy.load("pt_core_news_sm")

# Função principal
def preprocessar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-zA-Zá-úÁ-Ú0-9 ]", " ", texto)
    tokens = word_tokenize(texto)
    tokens = [palavra for palavra in tokens if palavra not in stop_words]
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc]

# ---------- CONFIGURAÇÃO -------------
# Saídas de 05 devem ficar em uma pasta separada
OUTPUT_FOLDER = "pipeline_output/05_pre"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ----- LEITURA DO ARQUIVO DE NOTÍCIAS -----
input_path = "./pipeline_output/01_03/noticias_processadas_15.json"
output_path = OUTPUT_FOLDER + "/noticias_pre_processadas_15.json"


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
