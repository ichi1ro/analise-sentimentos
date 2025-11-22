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
::   run_pipeline.cmd all
:: ============================================================

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

:: ----------------- Pipeline completo ------------------------
if "%1"=="all" goto :all

goto :help


:: ============================================================
:: FUNÇÃO: Instala dependências Python
:: ============================================================
:setup
echo ========================================
echo CONFIGURANDO AMBIENTE PYTHON
echo ========================================

:: Verifica se Python está instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3 primeiro.
    exit /b 1
)

echo Criando ambiente virtual (venv)...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install --upgrade pip
pip install pandas numpy yfinance beautifulsoup4 requests lxml nltk spacy matplotlib

echo Instalacao concluida!
echo Para ativar o ambiente depois, use:
echo   call venv\Scripts\activate.bat
exit /b 0



:: ============================================================
:: PASSO 1 — Coleta de Notícias
:: ============================================================
:fetch
echo.
echo ========================================
echo [1/4] Coletando noticias (01_fetch_raw.py)
echo ========================================
python 01_fetch_raw.py
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO ao executar 01_fetch_raw.py
    exit /b %ERRORLEVEL%
)
exit /b 0



:: ============================================================
:: PASSO 2 — Processamento de Notícias
:: ============================================================
:process
echo.
echo ========================================
echo [2/4] Processando noticias (02_process_raw.py)
echo ========================================
python 02_process_raw.py
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO ao executar 02_process_raw.py
    exit /b %ERRORLEVEL%
)
exit /b 0



:: ============================================================
:: PASSO 3 — Exportação para CSV
:: ============================================================
:exportcsv
echo.
echo ========================================
echo [3/4] Exportando CSV (03_export_csv.py)
echo ========================================
python 03_export_csv.py
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO ao executar 03_export_csv.py
    exit /b %ERRORLEVEL%
)
exit /b 0



:: ============================================================
:: PASSO 4 — Análise Financeira
:: ============================================================
:analyze
echo.
echo ========================================
echo [4/4] Analise Financeira (04_financial_analysis.py)
echo ========================================
python 04_financial_analysis.py
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO ao executar 04_financial_analysis.py
    exit /b %ERRORLEVEL%
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
echo.
echo ========================================
echo Pipeline executado com sucesso!
echo ========================================
exit /b 0



:: ============================================================
:: Ajuda
:: ============================================================
:help
echo.
echo Uso:
echo   run_pipeline.cmd setup     - Instala dependencias Python
echo   run_pipeline.cmd fetch     - Executa so a coleta
echo   run_pipeline.cmd process   - Executa so o processamento
echo   run_pipeline.cmd export    - Exporta CSV
echo   run_pipeline.cmd analyze   - Faz analise financeira
echo   run_pipeline.cmd all       - Roda tudo em ordem
echo.
exit /b 0
