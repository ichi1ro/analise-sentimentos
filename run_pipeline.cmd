@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: Pipeline de IA — Execução no Windows (CMD)
:: Suporta:
::   run_pipeline.cmd setup
::   run_pipeline.cmd fetch
::   run_pipeline.cmd process
::   run_pipeline.cmd export
::   run_pipeline.cmd analyze
::   run_pipeline.cmd textprep
::   run_pipeline.cmd sentiment
::   run_pipeline.cmd correlation
::   run_pipeline.cmd all
:: ============================================================

:: Diretórios usados
set "BASE_OUT=pipeline_output"
set "OUT_01_03=%BASE_OUT%\01_03"
set "OUT_04_FETCH=%BASE_OUT%\04_fetch"
set "OUT_05_PRE=%BASE_OUT%\05_pre"
set "OUT_06_SENTIMENT=%BASE_OUT%\06_sentiment"
set "OUT_07_COR=%BASE_OUT%\07_correlation"

:: Garantir diretórios existem
if not exist "%OUT_01_03%" mkdir "%OUT_01_03%" >nul 2>&1
if not exist "%OUT_04_FETCH%" mkdir "%OUT_04_FETCH%" >nul 2>&1
if not exist "%OUT_05_PRE%" mkdir "%OUT_05_PRE%" >nul 2>&1
if not exist "%OUT_06_SENTIMENT%" mkdir "%OUT_06_SENTIMENT%" >nul 2>&1
if not exist "%OUT_07_COR%" mkdir "%OUT_07_COR%" >nul 2>&1

:: ----------------- Função de ajuda --------------------------
if "%1"=="" goto :help
if "%1"=="help" goto :help

:: ----------------- Passo: Setup -----------------------------
if "%1"=="setup" goto :setup

:: ----------------- Passo 1: Fetch ---------------------------
if "%1"=="fetch" goto :fetch

:: ----------------- Passo 2: Process -------------------------
if "%1"=="process" goto :process

:: ----------------- Passo 3: Export --------------------------
if "%1"=="export" goto :exportcsv

:: ----------------- Passo 4: Analyze -------------------------
if "%1"=="analyze" goto :analyze

:: ----------------- Passo 5: Pré-processamento texto ---------
if "%1"=="textprep" goto :textprep

:: ----------------- Passo 6: Sentimento (06_sentiment_analysis.py) ---
if "%1"=="sentiment" goto :sentiment

:: ----------------- Passo 7: Correlação (07_correlation_analysis.py) ---
if "%1"=="correlation" goto :correlation

:: ----------------- Pipeline completo ------------------------
if "%1"=="all" goto :all

goto :help


:: ============================================================
:: FUNÇÃO: Instala dependências Python
:: Inclui pacotes para 06 (sentimento) e 07 (correlação)
:: ============================================================
:setup
echo ========================================
echo CONFIGURANDO AMBIENTE PYTHON
echo ========================================

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado no PATH.
    exit /b 1
)

echo Criando ambiente virtual (venv)...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install --upgrade pip
:: Pacotes comuns
pip install tls-client pandas numpy yfinance beautifulsoup4 requests lxml nltk spacy matplotlib seaborn scikit-learn openpyxl
:: Pacotes para sentiment e correlacao
pip install transformers torch torchvision torchaudio tqdm scipy

echo Instalando modelo SpaCy...
python -m spacy download pt_core_news_sm

echo Ambiente configurado com sucesso!
exit /b 0



:: ============================================================
:: PASSO 1 — Fetch
:: ============================================================
:fetch
echo.
echo =============== FETCH (01_fetch_raw.py) ===============
python 01_fetch_raw.py || (echo ERRO && exit /b)

:: Copia de outputs para a pasta consolidada (01_03)
IF EXIST "noticias_processadas.json" (
    copy /Y "noticias_processadas.json" "%OUT_01_03%" >nul
)
IF EXIST "raw_infomoney.json" (
    copy /Y "raw_infomoney.json" "%OUT_01_03%" >nul
)

exit /b 0



:: ============================================================
:: PASSO 2 — Process
:: ============================================================
:process
echo.
echo =============== PROCESS (02_process_raw.py) ===============
python 02_process_raw.py || (echo ERRO && exit /b)

:: Copia de outputs para a pasta consolidada (01_03)
IF EXIST "noticias_processadas.json" (
    copy /Y "noticias_processadas.json" "%OUT_01_03%" >nul
)

exit /b 0



:: ============================================================
:: PASSO 3 — Export CSV
:: ============================================================
:exportcsv
echo.
echo =============== EXPORT CSV (03_export_csv.py) ===============
python 03_export_csv.py || (echo ERRO && exit /b)

:: Copia de outputs para a pasta consolidada (01_03)
IF EXIST "%BASE_OUT%\finance_analysis_output\noticias_com_precos.csv" (
    copy /Y "%BASE_OUT%\finance_analysis_output\noticias_com_precos.csv" "%OUT_01_03%" >nul
)
IF EXIST "%BASE_OUT%\finance_analysis_output\noticias_com_precos_15.csv" (
    copy /Y "%BASE_OUT%\finance_analysis_output\noticias_com_precos_15.csv" "%OUT_01_03%" >nul
)
IF EXIST "%BASE_OUT%\finance_analysis_output\resumo_por_empresa.csv" (
    copy /Y "%BASE_OUT%\finance_analysis_output\resumo_por_empresa.csv" "%OUT_01_03%" >nul
)
IF EXIST "%BASE_OUT%\finance_analysis_output\resumo_por_empresa_15.csv" (
    copy /Y "%BASE_OUT%\finance_analysis_output\resumo_por_empresa_15.csv" "%OUT_01_03%" >nul
)

exit /b 0



:: ============================================================
:: PASSO 4 — Analyze
:: ============================================================
:analyze
echo.
echo =============== ANALYZE (04_financial_analysis.py) ===============
python 04_financial_analysis.py || (echo ERRO && exit /b %ERRORLEVEL%)

:: Copia de outputs para a pasta 04_fetch
IF EXIST "pipeline_output/noticias_com_precos.csv" (
    copy /Y "pipeline_output/noticias_com_precos.csv" "%OUT_04_FETCH%" >nul
)
IF EXIST "pipeline_output/noticias_com_precos_15.csv" (
    copy /Y "pipeline_output/noticias_com_precos_15.csv" "%OUT_04_FETCH%" >nul
)

:: Copia de outputs para 07 (corrigir conforme necessário)
IF EXIST "pipeline_output/07_correlation/dados_completos.csv" (
    copy /Y "pipeline_output/07_correlation/dados_completos.csv" "%OUT_07_COR%" >nul
)

exit /b 0



:: ============================================================
:: PASSO 5 — Pré-processamento texto
:: ============================================================
:textprep
echo.
echo =============== TEXT PREP (05_pre_processamento.py) ===============
python 05_pre_processamento.py || (echo ERRO && exit /b)

:: Copia do output do pré-processamento
IF EXIST "pipeline_output/05_pre/noticias_pre_processadas_15.json" (
    copy /Y "pipeline_output/05_pre/noticias_pre_processadas_15.json" "%OUT_05_PRE%" >nul
)

exit /b 0



:: ============================================================
:: PASSO 6 — Sentimento (06_sentiment_analysis.py)
:: ============================================================
:sentiment
echo.
echo =============== SENTIMENTO (06_sentiment_analysis.py) ===============
python 06_sentiment_analysis.py || (echo ERRO && exit /b %ERRORLEVEL%)

:: Copia outputs (se desejado) para consolidação
IF EXIST "pipeline_output/06_sentiment/noticias_com_sentimentos.json" (
    copy /Y "pipeline_output/06_sentiment/noticias_com_sentimentos.json" "%OUT_06_SENTIMENT%" >nul
)

exit /b 0



:: ============================================================
:: PASSO 7 — Correlação (07_correlation_analysis.py)
:: ============================================================
:correlation
echo.
echo =============== CORRELAÇÃO (07_correlation_analysis.py) ===============
python 07_correlation_analysis.py || (echo ERRO && exit /b %ERRORLEVEL%)

:: Copia outputs (se desejar) para consolidação
IF EXIST "pipeline_output/07_correlation/dados_completos.csv" (
    copy /Y "pipeline_output/07_correlation/dados_completos.csv" "%OUT_07_COR%" >nul
)

exit /b 0



:: ============================================================
:: PIPELINE COMPLETO
:: ============================================================
:all
call :fetch
call :process
call :exportcsv
call :analyze
call :textprep
call :sentiment
call :correlation

echo.
echo ========================================
echo PIPELINE EXECUTADO COM SUCESSO!
echo ========================================
exit /b 0



:: ============================================================
:: Ajuda
:: ============================================================
:help
echo.
echo Uso:
echo   run_pipeline.cmd setup
echo   run_pipeline.cmd fetch
echo   run_pipeline.cmd process
echo   run_pipeline.cmd export
echo   run_pipeline.cmd analyze
echo   run_pipeline.cmd textprep
echo   run_pipeline.cmd sentiment
echo   run_pipeline.cmd correlation
echo   run_pipeline.cmd all
echo.
exit /b 0