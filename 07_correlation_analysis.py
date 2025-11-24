#!/usr/bin/env python3
"""
07_correlation_analysis.py - Análise de Correlação Sentimento x Variação de Preços

Calcula correlação de Pearson entre scores de sentimento e variação de preços das ações,
conforme especificação do trabalho.

Funcionalidades:
1. Carrega sentimentos (com e sem pré-processamento) do arquivo JSON
2. Carrega variações de preços do CSV
3. Calcula correlação de Pearson
4. Gera visualizações (scatter plots, time series)
5. Salva resultados e estatísticas
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import os

# ---------- CONFIGURAÇÃO ----------
INPUT_SENTIMENT = "pipeline_output/06_sentiment/noticias_com_sentimentos.json"
INPUT_PRICES = "pipeline_output/04_fetch/noticias_com_precos_civis.csv"
OUTPUT_FOLDER = "pipeline_output/07_correlation"
OUTPUT_STATS = os.path.join(OUTPUT_FOLDER, "estatisticas_correlacao.txt")
OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "dados_completos.csv")

# Criar pasta de saída
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configuração de estilo para gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print(f"\n{'='*60}")
print("ANÁLISE DE CORRELAÇÃO: SENTIMENTO x VARIAÇÃO DE PREÇOS")
print(f"{'='*60}\n")
print(f"Entrada sentimentos: {INPUT_SENTIMENT}")
print(f"Entrada preços: {INPUT_PRICES}")
print(f"Saída: {OUTPUT_FOLDER}\n")

# ---------- CARREGAR DADOS ----------

print("📂 Carregando dados de sentimento...")
with open(INPUT_SENTIMENT, 'r', encoding='utf-8') as f:
    noticias_sentiment = json.load(f)
print(f"✅ {len(noticias_sentiment)} notícias com sentimento carregadas\n")

print("📂 Carregando dados de preços...")
df_prices = pd.read_csv(INPUT_PRICES, encoding='utf-8', sep=';')
print(f"✅ {len(df_prices)} registros de preços carregados\n")

# ---------- PREPARAR DADOS (JOIN mais robusto) ----------

print("🔄 Preparando dados para análise...")

# Normalizar sentimento para DataFrame
df_sent = pd.DataFrame(noticias_sentiment)

# Garantir colunas necessárias: data_publicacao como date, url (opcional)
if 'data_publicacao' in df_sent.columns:
    df_sent['data_publicacao'] = pd.to_datetime(df_sent['data_publicacao'], errors='coerce').dt.date
else:
    df_sent['data_publicacao'] = pd.NaT

# Normalizar preços
df_prices = df_prices.copy()
if 'data_publicacao' in df_prices.columns:
    df_prices['data_publicacao'] = pd.to_datetime(df_prices['data_publicacao'], errors='coerce').dt.date
else:
    df_prices['data_publicacao'] = pd.NaT

# Tenta junção pelo máximo de robustez:
# 1) se houver URL em ambos, faz merge por empresa + url
# 2) senão, merge por empresa + data_publicacao
has_url_sent = 'url' in df_sent.columns
has_url_prices = 'url' in df_prices.columns

if has_url_sent and has_url_prices:
    merged = pd.merge(
        df_sent,
        df_prices,
        how='left',
        left_on=['empresa', 'url'],
        right_on=['empresa', 'url'],
        suffixes=('_sent', '_price')
    )
else:
    merged = pd.merge(
        df_sent,
        df_prices,
        how='left',
        left_on=['empresa', 'data_publicacao'],
        right_on=['empresa', 'data_publicacao'],
        suffixes=('__sent', '_price')
    )

# Detecção de colunas de variação de preço
# As colunas costumam vir como: d-2_pct_change_prev_close, d-1_pct_change_prev_close, d+0_pct_change_prev_close, etc.
price_variation_cols = [c for c in merged.columns if c.endswith('_pct_change_prev_close')]
variacoes_map = {}  # map: periodo -> coluna original
periodos = ['d-2', 'd-1', 'd+0', 'd+1', 'd+2']  # manter formato que deve aparecer no CSV
for col in price_variation_cols:
    # extrair o periodo do nome da coluna
    # exemplo: 'd-2_pct_change_prev_close' -> 'd-2'
    periodo = col.replace('_pct_change_prev_close', '')
    variacoes_map[periodo] = col

# Adicionar colunas padronizadas de variação
for periodo, col in variacoes_map.items():
    merged[f'variacao_{periodo}'] = merged[col]

# Selecionar apenas as colunas necessárias para o DataFrame final
variacao_columns_present = [f'variacao_{p}' for p in periodos if f'variacao_{p}' in merged.columns]
selected_cols = ['empresa', 'titulo', 'data_publicacao', 'sentimento_original', 'sentimento_preprocessado'] + variacao_columns_present

df = merged.reindex(columns=selected_cols)

# Tratar título caso não exista
if 'titulo' not in df.columns:
    df['titulo'] = ''

# Filtrar notícias com dados completos (sentimento + preços)
df_complete = df.dropna(subset=[c for c in df.columns if c.startswith('variacao_')], how='any')
print(f"✅ {len(df_complete)} notícias com dados completos (sentimento + preços)\n")

# Salvar dados unificados
df_complete.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
print(f"💾 Dados completos salvos em: {OUTPUT_CSV}\n")

# ---------- ANÁLISE DE CORRELAÇÃO ----------

print(f"{'='*60}")
print("CÁLCULO DE CORRELAÇÕES DE PEARSON")
print(f"{'='*60}\n")

# Colunas de variação de preço (as ones disponíveis)
colunas_variacao = [col for col in df_complete.columns if col.startswith('variacao_')]

# Resultados de correlação
resultados = []

with open(OUTPUT_STATS, 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("ANÁLISE DE CORRELAÇÃO: SENTIMENTO x VARIAÇÃO DE PREÇOS\n")
    f.write("="*60 + "\n\n")

    # 1. Correlação SENTIMENTO ORIGINAL vs VARIAÇÕES
    f.write("1. SENTIMENTO ORIGINAL (sem pré-processamento)\n")
    f.write("-" * 60 + "\n\n")

    for col_var in colunas_variacao:
        mask = df_complete[col_var].notna()
        x = df_complete.loc[mask, 'sentimento_original']
        y = df_complete.loc[mask, col_var]

        if len(x) >= 3:
            corr, p_value = pearsonr(x, y)

            resultado = {
                'tipo': 'Original',
                'periodo': col_var,
                'correlacao': corr,
                'p_value': p_value,
                'n_amostras': len(x),
                'significativo': 'Sim' if p_value < 0.05 else 'Não'
            }
            resultados.append(resultado)

            f.write(f"  {col_var}:\n")
            f.write(f"    Correlação de Pearson: {corr:.4f}\n")
            f.write(f"    P-valor: {p_value:.4f}\n")
            f.write(f"    Amostras: {len(x)}\n")
            f.write(f"    Significativo (p<0.05): {resultado['significativo']}\n\n")

    f.write("\n")

    # 2. Correlação SENTIMENTO PRÉ-PROCESSADO vs VARIAÇÕES
    f.write("2. SENTIMENTO PRÉ-PROCESSADO\n")
    f.write("-" * 60 + "\n\n")

    for col_var in colunas_variacao:
        mask = df_complete[col_var].notna()
        x = df_complete.loc[mask, 'sentimento_preprocessado']
        y = df_complete.loc[mask, col_var]

        if len(x) >= 3:
            corr, p_value = pearsonr(x, y)

            resultado = {
                'tipo': 'Pré-processado',
                'periodo': col_var,
                'correlacao': corr,
                'p_value': p_value,
                'n_amostras': len(x),
                'significativo': 'Sim' if p_value < 0.05 else 'Não'
            }
            resultados.append(resultado)

            f.write(f"  {col_var}:\n")
            f.write(f"    Correlação de Pearson: {corr:.4f}\n")
            f.write(f"    P-valor: {p_value:.4f}\n")
            f.write(f"    Amostras: {len(x)}\n")
            f.write(f"    Significativo (p<0.05): {resultado['significativo']}\n\n")

    f.write("\n")
    f.write("="*60 + "\n")
    f.write("RESUMO\n")
    f.write("="*60 + "\n\n")

    # Resumo: melhores correlações
    df_resultados = pd.DataFrame(resultados)

    f.write("MELHORES CORRELAÇÕES (por valor absoluto):\n\n")
    if not df_resultados.empty:
        top_correlacoes = df_resultados.nlargest(5, 'correlacao', keep='all')
        for idx, row in top_correlacoes.iterrows():
            f.write(f"  {row['tipo']} - {row['periodo']}: {row['correlacao']:.4f} ")
            f.write(f"(p={row['p_value']:.4f}, n={row['n_amostras']})\n")
    else:
        f.write("Nenhuma correlação significativa calculada.\n")

    f.write("\n")

    # Média de correlações por tipo
    if not df_resultados.empty:
        media_original = df_resultados[df_resultados['tipo'] == 'Original']['correlacao'].mean()
        media_prep = df_resultados[df_resultados['tipo'] == 'Pré-processado']['correlacao'].mean()
    else:
        media_original = float('nan')
        media_prep = float('nan')

    f.write(f"MÉDIA DE CORRELAÇÕES:\n")
    f.write(f"  Original: {media_original:.4f}\n")
    f.write(f"  Pré-processado: {media_prep:.4f}\n\n")

    # Correlações significativas
    if not df_resultados.empty:
        sig_original = len(df_resultados[(df_resultados['tipo'] == 'Original') & (df_resultados['p_value'] < 0.05)])
        sig_prep = len(df_resultados[(df_resultados['tipo'] == 'Pré-processado') & (df_resultados['p_value'] < 0.05)])
    else:
        sig_original = 0
        sig_prep = 0

    f.write(f"CORRELAÇÕES SIGNIFICATIVAS (p<0.05):\n")
    f.write(f"  Original: {sig_original}/{len(colunas_variacao)}\n")
    f.write(f"  Pré-processado: {sig_prep}/{len(colunas_variacao)}\n\n")

print(f"💾 Estatísticas salvas em: {OUTPUT_STATS}\n")

# Imprimir resumo no console
print("RESUMO DAS CORRELALAÇÕES:")
print("-" * 60)
if 'media_original' in locals() and 'media_prep' in locals():
    print(f"Média de correlação (Original): {media_original:.4f}")
    print(f"Média de correlação (Pré-processado): {media_prep:.4f}")
else:
    print("Médias não disponíveis (sem dados de correlação).")
if 'sig_original' in locals() and 'sig_prep' in locals():
    print(f"Correlações significativas (Original): {sig_original}/{len(colunas_variacao)}")
    print(f"Correlações significativas (Pré-processado): {sig_prep}/{len(colunas_variacao)}\n")
else:
    print("Correlações significativas não disponíveis.\n")

# ---------- VISUALIZAÇÕES ----------

print(f"{'='*60}")
print("GERANDO VISUALIZAÇÕES")
print(f"{'='*60}\n")

# 1. Scatter plot: Sentimento vs Variação D+1 (próximo pregão)
print("📊 Gerando scatter plot (Sentimento vs Variação D+1)...")

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Original
mask = df_complete['variacao_d+1'].notna()
x_orig = df_complete.loc[mask, 'sentimento_original']
y_orig = df_complete.loc[mask, 'variacao_d+1']
corr_orig, p_orig = pearsonr(x_orig, y_orig) if len(x_orig) >= 3 else (0, 1)

axes[0].scatter(x_orig, y_orig, alpha=0.6, s=100, color='steelblue')
axes[0].set_xlabel('Sentimento Original', fontsize=12)
axes[0].set_ylabel('Variação de Preço D+1 (%)', fontsize=12)
axes[0].set_title(f'Original: r={corr_orig:.4f}, p={p_orig:.4f}', fontsize=14)
axes[0].grid(True, alpha=0.3)
axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axes[0].axvline(x=0, color='red', linestyle='--', alpha=0.5)

# Pré-processado
x_prep = df_complete.loc[mask, 'sentimento_preprocessado']
y_prep = df_complete.loc[mask, 'variacao_d+1']
corr_prep, p_prep = pearsonr(x_prep, y_prep) if len(x_prep) >= 3 else (0, 1)

axes[1].scatter(x_prep, y_prep, alpha=0.6, s=100, color='darkorange')
axes[1].set_xlabel('Sentimento Pré-processado', fontsize=12)
axes[1].set_ylabel('Variação de Preço D+1 (%)', fontsize=12)
axes[1].set_title(f'Pré-processado: r={corr_prep:.4f}, p={p_prep:.4f}', fontsize=14)
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axes[1].axvline(x=0, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'scatter_sentimento_vs_variacao_d+1.png'), dpi=300)
plt.close()
print("✅ Scatter plot salvo\n")

# 2. Heatmap de correlações
print("📊 Gerando heatmap de correlações...")

# Preparar matriz de correlações
periodos = ['d-2', 'd-1', 'd+0', 'd+1', 'd+2']
matriz_corr = np.zeros((2, len(periodos)))

for i, periodo in enumerate(periodos):
    col = f'variacao_{periodo}'
    if col in df_complete.columns:
        mask = df_complete[col].notna()

        # Original
        if len(df_complete.loc[mask, 'sentimento_original']) >= 3:
            corr_orig, _ = pearsonr(df_complete.loc[mask, 'sentimento_original'], df_complete.loc[mask, col])
            matriz_corr[0, i] = corr_orig

        # Pré-processado
        if len(df_complete.loc[mask, 'sentimento_preprocessado']) >= 3:
            corr_prep, _ = pearsonr(df_complete.loc[mask, 'sentimento_preprocessado'], df_complete.loc[mask, col])
            matriz_corr[1, i] = corr_prep

fig, ax = plt.subplots(figsize=(10, 4))
sns.heatmap(matriz_corr, annot=True, fmt='.4f', cmap='RdYlGn', center=0,
            xticklabels=periodos, yticklabels=['Original', 'Pré-processado'],
            cbar_kws={'label': 'Correlação de Pearson'})
ax.set_title('Correlações: Sentimento x Variação de Preços por Período', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'heatmap_correlacoes.png'), dpi=300)
plt.close()
print("✅ Heatmap salvo\n")

# 3. Gráfico de barras: comparação de correlações
print("📊 Gerando gráfico de barras (comparação)...")

fig, ax = plt.subplots(figsize=(12, 6))
x_pos = np.arange(len(periodos))
width = 0.35

corr_original = matriz_corr[0, :]
corr_prep = matriz_corr[1, :]

bars1 = ax.bar(x_pos - width/2, corr_original, width, label='Original', color='steelblue', alpha=0.8)
bars2 = ax.bar(x_pos + width/2, corr_prep, width, label='Pré-processado', color='darkorange', alpha=0.8)

ax.set_xlabel('Período', fontsize=12)
ax.set_ylabel('Correlação de Pearson', fontsize=12)
ax.set_title('Comparação de Correlações: Original vs Pré-processado', fontsize=14)
ax.set_xticks(x_pos)
ax.set_xticklabels(periodos)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'barras_comparacao_correlacoes.png'), dpi=300)
plt.close()
print("✅ Gráfico de barras salvo\n")

# 4. Box plot: distribuição de sentimentos por empresa
print("📊 Gerando box plots (distribuição por empresa)...")

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Original
df_complete.boxplot(column='sentimento_original', by='empresa', ax=axes[0])
axes[0].set_title('Distribuição de Sentimento Original por Empresa', fontsize=12)
axes[0].set_xlabel('Empresa', fontsize=11)
axes[0].set_ylabel('Sentimento', fontsize=11)
axes[0].get_figure().suptitle('')  # Remove título automático

# Pré-processado
df_complete.boxplot(column='sentimento_preprocessado', by='empresa', ax=axes[1])
axes[1].set_title('Distribuição de Sentimento Pré-processado por Empresa', fontsize=12)
axes[1].set_xlabel('Empresa', fontsize=11)
axes[1].set_ylabel('Sentimento', fontsize=11)
axes[1].get_figure().suptitle('')  # Remove título automático

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'boxplot_sentimento_por_empresa.png'), dpi=300)
plt.close()
print("✅ Box plots salvos\n")

# ---------- FINALIZAÇÃO ----------

print(f"{'='*60}")
print("✅ ANÁLISE DE CORRELAÇÃO CONCLUÍDA!")
print(f"{'='*60}\n")
print("Arquivos gerados:")
print(f"  - {OUTPUT_STATS}")
print(f"  - {OUTPUT_CSV}")
print(f"  - {OUTPUT_FOLDER}/scatter_sentimento_vs_variacao_d+1.png")
print(f"  - {OUTPUT_FOLDER}/heatmap_correlacoes.png")
print(f"  - {OUTPUT_FOLDER}/barras_comparacao_correlacoes.png")
print(f"  - {OUTPUT_FOLDER}/boxplot_sentimento_por_empresa.png")
print()