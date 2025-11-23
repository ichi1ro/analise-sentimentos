#!/bin/bash

# ============================================================
# Pipeline de IA — Execução no Linux (Bash)
# Suporta:
#   ./run_pipeline.sh setup
#   ./run_pipeline.sh fetch
#   ./run_pipeline.sh process
#   ./run_pipeline.sh export
#   ./run_pipeline.sh analyze
#   ./run_pipeline.sh textprep
#   ./run_pipeline.sh all
# ============================================================

# Diretórios usados
BASE_OUT="pipeline_output"
OUT_01_03="$BASE_OUT/01_03"
OUT_04_FETCH="$BASE_OUT/04_fetch"
OUT_05_PRE="$BASE_OUT/05_pre"

# Garantir diretórios existem
mkdir -p "$OUT_01_03" 2>/dev/null
mkdir -p "$OUT_04_FETCH" 2>/dev/null
mkdir -p "$OUT_05_PRE" 2>/dev/null

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python do venv
VENV_PYTHON="./venv/bin/python"

# Função para verificar se venv existe
check_venv() {
    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${RED}ERRO: Ambiente virtual não encontrado!${NC}"
        echo "Execute primeiro: ./run_pipeline.sh setup"
        exit 1
    fi
}

# ----------------- Função de ajuda --------------------------
show_help() {
    echo ""
    echo "Uso:"
    echo "  ./run_pipeline.sh setup     - Instala dependências Python"
    echo "  ./run_pipeline.sh fetch     - Executa só a coleta"
    echo "  ./run_pipeline.sh process   - Executa só o processamento"
    echo "  ./run_pipeline.sh export    - Exporta CSV"
    echo "  ./run_pipeline.sh analyze   - Faz análise financeira"
    echo "  ./run_pipeline.sh textprep  - Pré-processa o texto para IA / Sentimento"
    echo "  ./run_pipeline.sh all       - Roda tudo em ordem"
    echo ""
    echo "Observação:"
    echo "- Saídas do 01/02/03 passam para: $BASE_OUT/01_03"
    echo "- Saídas do 04 são salvas em: $BASE_OUT/04_fetch"
    echo "- Saídas do 05 são salvas em: $BASE_OUT/05_pre"
    echo ""
}

# ============================================================
# FUNÇÃO: Instala dependências Python
# ============================================================
setup() {
    echo "========================================"
    echo "CONFIGURANDO AMBIENTE PYTHON"
    echo "========================================"

    # Verifica se Python está instalado
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERRO: Python3 não encontrado.${NC}"
        echo "Instale Python 3 primeiro."
        exit 1
    fi

    echo "Criando ambiente virtual (venv)..."
    python3 -m venv venv

    echo "Ativando ambiente virtual..."
    source venv/bin/activate

    echo "Instalando dependências..."
    pip install --upgrade pip
    pip install tls-client pandas numpy yfinance beautifulsoup4 requests lxml nltk spacy matplotlib seaborn scikit-learn

    echo "Instalando modelo de linguagem do spaCy..."
    python3 -m spacy download pt_core_news_sm

    echo -e "${GREEN}Instalação concluída!${NC}"
    echo "Para ativar o ambiente depois, use:"
    echo "  source venv/bin/activate"
}

# ============================================================
# PASSO 1 — Fetch (Coleta de Notícias)
# ============================================================
fetch() {
    check_venv
    echo ""
    echo "========================================"
    echo "[1/5] Coletando notícias (01_fetch_raw.py)"
    echo "========================================"

    $VENV_PYTHON 01_fetch_raw.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO ao executar 01_fetch_raw.py${NC}"
        exit $?
    fi

    # Copia de outputs para a pasta consolidada (01_03)
    [ -f "noticias_processadas.json" ] && cp "noticias_processadas.json" "$OUT_01_03/noticias_processadas.json"
    [ -f "raw_infomoney.json" ] && cp "raw_infomoney.json" "$OUT_01_03/raw_infomoney.json"
}

# ============================================================
# PASSO 2 — Processamento (02_process_raw.py)
# ============================================================
process() {
    check_venv
    echo ""
    echo "========================================"
    echo "[2/5] Processando notícias (02_process_raw.py)"
    echo "========================================"

    $VENV_PYTHON 02_process_raw.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO ao executar 02_process_raw.py${NC}"
        exit $?
    fi

    # Copia de outputs para a pasta consolidada (01_03)
    [ -f "noticias_processadas.json" ] && cp "noticias_processadas.json" "$OUT_01_03/noticias_processadas.json"
}

# ============================================================
# PASSO 3 — Exportação para CSV (03_export_csv.py)
# ============================================================
export_csv() {
    check_venv
    echo ""
    echo "========================================"
    echo "[3/5] Exportando CSV (03_export_csv.py)"
    echo "========================================"

    $VENV_PYTHON 03_export_csv.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO ao executar 03_export_csv.py${NC}"
        exit $?
    fi

    # Copia de outputs para a pasta consolidada (01_03)
    [ -f "$BASE_OUT/finance_analysis_output/noticias_com_precos.csv" ] && \
        cp "$BASE_OUT/finance_analysis_output/noticias_com_precos.csv" "$OUT_01_03/noticias_com_precos.csv"
    [ -f "$BASE_OUT/finance_analysis_output/resumo_por_empresa.csv" ] && \
        cp "$BASE_OUT/finance_analysis_output/resumo_por_empresa.csv" "$OUT_01_03/resumo_por_empresa.csv"
}

# ============================================================
# PASSO 4 — Análise Financeira
# ============================================================
analyze() {
    check_venv
    echo ""
    echo "========================================"
    echo "[4/5] Análise Financeira (04_financial_analysis.py)"
    echo "========================================"

    $VENV_PYTHON 04_financial_analysis.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO ao executar 04_financial_analysis.py${NC}"
        exit $?
    fi

    # Copia de outputs para a pasta de 04_fetch
    [ -f "pipeline_output/noticias_com_precos.csv" ] && \
        cp "pipeline_output/noticias_com_precos.csv" "$OUT_04_FETCH/noticias_com_precos.csv"
    [ -f "pipeline_output/resumo_por_empresa.csv" ] && \
        cp "pipeline_output/resumo_por_empresa.csv" "$OUT_04_FETCH/resumo_por_empresa.csv"
}

# ============================================================
# PASSO 5 — Pré-processamento de texto para Sentimento
# ============================================================
textprep() {
    check_venv
    echo ""
    echo "========================================"
    echo "[5/5] Pré-processamento de texto (05_pre_processamento.py)"
    echo "========================================"

    $VENV_PYTHON 05_pre_processamento.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO ao executar 05_pre_processamento.py${NC}"
        exit $?
    fi

    # Copia o arquivo final para a pasta consolidada
    [ -f "01_03/noticias_processadas_15_PROCESSADAS.json" ] && \
        cp "01_03/noticias_processadas_15_PROCESSADAS.json" "$OUT_01_03/noticias_processadas_15_PROCESSADAS.json"

    echo -e "${GREEN}Texto pré-processado com sucesso!${NC}"
}

# ============================================================
# PIPELINE COMPLETO
# ============================================================
run_all() {
    fetch
    process
    export_csv
    analyze
    textprep
    echo ""
    echo "========================================"
    echo -e "${GREEN}Pipeline executado com sucesso!${NC}"
    echo "========================================"
}

# ============================================================
# Processamento de argumentos
# ============================================================
case "${1:-help}" in
    setup)
        setup
        ;;
    fetch)
        fetch
        ;;
    process)
        process
        ;;
    export)
        export_csv
        ;;
    analyze)
        analyze
        ;;
    textprep)
        textprep
        ;;
    all)
        run_all
        ;;
    help|*)
        show_help
        ;;
esac
