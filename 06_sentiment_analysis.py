#!/usr/bin/env python3
"""
06_sentiment_analysis.py - Análise de Sentimentos com BERT

Implementa análise de sentimentos usando modelo BERT pré-treinado em português,
conforme especificação do trabalho (Transformers: BERT).

Funcionalidades:
1. Análise COM pré-processamento (texto limpo)
2. Análise SEM pré-processamento (texto original)
3. Mapeamento de sentimentos para escala -10 a +10
4. Comparação entre as duas abordagens
"""

import json
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

# ---------- CONFIGURAÇÃO ----------
INPUT_ORIGINAL = "pipeline_output/01_03/noticias_processadas_15.json"
INPUT_PREPROCESSED = "pipeline_output/05_pre/noticias_pre_processadas_15.json"
OUTPUT_FOLDER = "pipeline_output/06_sentiment"
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "noticias_com_sentimentos.json")
COMPARACAO_FILE = os.path.join(OUTPUT_FOLDER, "comparacao_preprocessamento.txt")

# Criar pasta de saída
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Modelo BERT pré-treinado em português
# Opções testadas:
# 1. "neuralmind/bert-base-portuguese-cased" - BERT base português
# 2. "lxyuan/distilbert-base-multilingual-cased-sentiments-student" - Multilingual
MODEL_NAME = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"

print(f"\n{'='*60}")
print("ANÁLISE DE SENTIMENTOS COM BERT")
print(f"{'='*60}\n")
print(f"Modelo: {MODEL_NAME}")
print(f"Entrada original: {INPUT_ORIGINAL}")
print(f"Entrada pré-processada: {INPUT_PREPROCESSED}")
print(f"Saída: {OUTPUT_FILE}\n")

# ---------- FUNÇÕES AUXILIARES ----------

def mapear_sentimento_para_escala(label, score):
    """
    Mapeia o resultado do BERT para escala -10 a +10

    Args:
        label: 'positive', 'negative', ou 'neutral'
        score: confiança do modelo (0.0 a 1.0)

    Returns:
        float: sentimento entre -10 e +10
    """
    label_lower = label.lower()

    if label_lower == 'positive':
        return score * 10
    elif label_lower == 'negative':
        return -score * 10
    else:  # neutral
        return 0.0


def analisar_sentimento(texto, analyzer, max_length=512):
    """
    Analisa o sentimento de um texto usando BERT

    Args:
        texto: string com o conteúdo
        analyzer: pipeline do transformers
        max_length: tamanho máximo de tokens (BERT = 512)

    Returns:
        float: sentimento entre -10 e +10
    """
    if not texto or len(texto.strip()) == 0:
        return 0.0

    try:
        # Pipeline do transformers já faz truncation automaticamente
        resultado = analyzer(texto, truncation=True, max_length=max_length)[0]
        sentimento = mapear_sentimento_para_escala(
            resultado['label'],
            resultado['score']
        )
        return round(sentimento, 2)
    except Exception as e:
        print(f"⚠️  Erro ao analisar texto: {str(e)[:100]}")
        return 0.0


def carregar_noticias(filepath):
    """Carrega notícias do arquivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def reconstruir_texto_preprocessado(tokens):
    """
    Reconstrói texto a partir de tokens pré-processados

    Args:
        tokens: lista de tokens (palavras lematizadas)

    Returns:
        string: texto reconstruído
    """
    if isinstance(tokens, list):
        return " ".join(tokens)
    return str(tokens)


# ---------- PROCESSAMENTO PRINCIPAL ----------

def main():
    print("🔄 Carregando modelo BERT...")

    # Carregar modelo de análise de sentimentos
    # Forçar CPU (device=-1) devido a incompatibilidade da GPU GTX 1050 Ti
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        device=-1  # CPU (mais lento mas funciona em qualquer hardware)
    )

    print(f"✅ Modelo carregado (Device: {'GPU' if torch.cuda.is_available() else 'CPU'})\n")

    # Carregar notícias originais
    print("📂 Carregando notícias originais...")
    noticias = carregar_noticias(INPUT_ORIGINAL)
    print(f"✅ {len(noticias)} notícias carregadas\n")

    # ANÁLISE 1: Texto ORIGINAL (sem pré-processamento)
    print("🔍 ANÁLISE 1: Texto ORIGINAL (sem pré-processamento)")
    print("-" * 60)

    for noticia in tqdm(noticias, desc="Processando"):
        conteudo_original = noticia.get('conteudo', '')
        sentimento = analisar_sentimento(conteudo_original, sentiment_analyzer)
        noticia['sentimento_original'] = sentimento

    print("✅ Análise de texto original concluída\n")

    # ANÁLISE 2: Texto PRÉ-PROCESSADO (se disponível)
    print("🔍 ANÁLISE 2: Texto PRÉ-PROCESSADO")
    print("-" * 60)

    if os.path.exists(INPUT_PREPROCESSED):
        print(f"📂 Carregando notícias pré-processadas...")
        noticias_prep = carregar_noticias(INPUT_PREPROCESSED)

        # Criar mapeamento por empresa + título
        prep_map = {}
        for n in noticias_prep:
            key = (n['empresa'], n['titulo'])
            prep_map[key] = n.get('conteudo_processado', [])

        # Analisar textos pré-processados
        for noticia in tqdm(noticias, desc="Processando"):
            key = (noticia['empresa'], noticia['titulo'])

            if key in prep_map:
                tokens = prep_map[key]
                texto_limpo = reconstruir_texto_preprocessado(tokens)
                sentimento = analisar_sentimento(texto_limpo, sentiment_analyzer)
                noticia['sentimento_preprocessado'] = sentimento
            else:
                noticia['sentimento_preprocessado'] = noticia['sentimento_original']

        print("✅ Análise de texto pré-processado concluída\n")
    else:
        print(f"⚠️  Arquivo pré-processado não encontrado: {INPUT_PREPROCESSED}")
        print("   Pulando análise com pré-processamento\n")

        # Copiar sentimento original para pré-processado
        for noticia in noticias:
            noticia['sentimento_preprocessado'] = noticia['sentimento_original']

    # Salvar resultados
    print(f"💾 Salvando resultados em: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(noticias, f, indent=2, ensure_ascii=False)

    print("✅ Resultados salvos\n")

    # ---------- ESTATÍSTICAS E COMPARAÇÃO ----------

    print(f"{'='*60}")
    print("ESTATÍSTICAS")
    print(f"{'='*60}\n")

    sentimentos_orig = [n['sentimento_original'] for n in noticias]
    sentimentos_prep = [n['sentimento_preprocessado'] for n in noticias]

    # Estatísticas descritivas
    stats_orig = {
        'media': sum(sentimentos_orig) / len(sentimentos_orig),
        'minimo': min(sentimentos_orig),
        'maximo': max(sentimentos_orig),
        'positivos': len([s for s in sentimentos_orig if s > 0]),
        'negativos': len([s for s in sentimentos_orig if s < 0]),
        'neutros': len([s for s in sentimentos_orig if s == 0])
    }

    stats_prep = {
        'media': sum(sentimentos_prep) / len(sentimentos_prep),
        'minimo': min(sentimentos_prep),
        'maximo': max(sentimentos_prep),
        'positivos': len([s for s in sentimentos_prep if s > 0]),
        'negativos': len([s for s in sentimentos_prep if s < 0]),
        'neutros': len([s for s in sentimentos_prep if s == 0])
    }

    # Imprimir estatísticas
    print("Texto ORIGINAL:")
    print(f"  Média: {stats_orig['media']:.2f}")
    print(f"  Mínimo: {stats_orig['minimo']:.2f} | Máximo: {stats_orig['maximo']:.2f}")
    print(f"  Positivos: {stats_orig['positivos']} | Negativos: {stats_orig['negativos']} | Neutros: {stats_orig['neutros']}")
    print()

    print("Texto PRÉ-PROCESSADO:")
    print(f"  Média: {stats_prep['media']:.2f}")
    print(f"  Mínimo: {stats_prep['minimo']:.2f} | Máximo: {stats_prep['maximo']:.2f}")
    print(f"  Positivos: {stats_prep['positivos']} | Negativos: {stats_prep['negativos']} | Neutros: {stats_prep['neutros']}")
    print()

    # Diferença média
    diferencas = [abs(o - p) for o, p in zip(sentimentos_orig, sentimentos_prep)]
    diff_media = sum(diferencas) / len(diferencas)
    print(f"Diferença média absoluta: {diff_media:.2f}")
    print()

    # Salvar comparação em arquivo
    with open(COMPARACAO_FILE, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("COMPARAÇÃO: ORIGINAL vs PRÉ-PROCESSADO\n")
        f.write("="*60 + "\n\n")

        f.write("TEXTO ORIGINAL:\n")
        f.write(f"  Média: {stats_orig['media']:.2f}\n")
        f.write(f"  Mínimo: {stats_orig['minimo']:.2f} | Máximo: {stats_orig['maximo']:.2f}\n")
        f.write(f"  Positivos: {stats_orig['positivos']} | Negativos: {stats_orig['negativos']} | Neutros: {stats_orig['neutros']}\n\n")

        f.write("TEXTO PRÉ-PROCESSADO:\n")
        f.write(f"  Média: {stats_prep['media']:.2f}\n")
        f.write(f"  Mínimo: {stats_prep['minimo']:.2f} | Máximo: {stats_prep['maximo']:.2f}\n")
        f.write(f"  Positivos: {stats_prep['positivos']} | Negativos: {stats_prep['negativos']} | Neutros: {stats_prep['neutros']}\n\n")

        f.write(f"Diferença média absoluta: {diff_media:.2f}\n\n")

        f.write("="*60 + "\n")
        f.write("AMOSTRAS (primeiras 10 notícias)\n")
        f.write("="*60 + "\n\n")

        for i, n in enumerate(noticias[:10]):
            f.write(f"[{i+1}] {n['empresa']} - {n['titulo'][:60]}...\n")
            f.write(f"    Original: {n['sentimento_original']:+.2f} | Pré-processado: {n['sentimento_preprocessado']:+.2f}\n\n")

    print(f"💾 Comparação salva em: {COMPARACAO_FILE}")
    print()

    # Exemplo de notícias
    print(f"{'='*60}")
    print("EXEMPLOS")
    print(f"{'='*60}\n")

    for i, n in enumerate(noticias[:3]):
        print(f"[{i+1}] {n['empresa']}")
        print(f"Título: {n['titulo'][:70]}...")
        print(f"Sentimento Original: {n['sentimento_original']:+.2f}")
        print(f"Sentimento Pré-processado: {n['sentimento_preprocessado']:+.2f}")
        print()

    print(f"{'='*60}")
    print("✅ ANÁLISE DE SENTIMENTOS CONCLUÍDA!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
