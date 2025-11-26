# Pipeline IA - Guia de Execução no Windows (CMD)

Este README descreve como rodar o pipeline de IA no Windows usando o script CMD fornecido. O workflow é dividido em etapas (setup, fetch, process, export, analyze, text-prep, sentiment, correlação) e pode ser executado como um todo ou por etapas. Entre no ambiente virtual do python gerado pelo passo de setup, e depois rode o comando para entrar no ambiente virtual: venv\Scripts\activate.bat

## 1) Visão geral
- Fluxo: Setup -> Fetch -> Process -> Export -> Analyze -> Textprep -> Sentiment -> Correlation -> All
- Usa um ambiente virtual Python (venv) criado pelo script.
- Saídas ficam em pipeline_output (com dados, estatísticas, gráficos e CSVs consolidados).

## 2) Requisitos
- Windows 10/11 (CMD)
- Python 3.8+ disponível no PATH
- Acesso à internet para instalar dependências (durante o setup)
- Permissões para criar pastas e o ambiente virtual no diretório do projeto

## 3) Estrutura de diretórios (cria automaticamente)
- pipeline_output
  - pipeline_output/01_03
  - pipeline_output/04_fetch
  - pipeline_output/05_pre
  - pipeline_output/06_sentiment
  - pipeline_output/07_correlation

Observação: os scripts já coordenam cópias para as pastas consolidando outputs intermediários.

## 4) Como usar (passo a passo)

Abra o CMD e navegue até o diretório do seu projeto. Use os comandos abaixo conforme desejado.

- Setup (uma única vez por ambiente)
  - Descrição: cria o virtualenv, instala dependências e configura o ambiente.
  - Comando:
    run_pipeline.cmd setup

- Fetch
  - Descrição: executa 01_fetch_raw.py para obter dados brutos.
  - Comando:
    run_pipeline.cmd fetch

- Process
  - Descrição: executa 02_process_raw.py para processar dados brutos.
  - Comando:
    run_pipeline.cmd process

- Export CSV
  - Descrição: executa 03_export_csv.py para exportar dados em CSV consolidado.
  - Comando:
    run_pipeline.cmd export

- Analyze
  - Descrição: executa 04_financial_analysis.py para análises financeiras iniciais.
  - Comando:
    run_pipeline.cmd analyze

- Text Prep (Pré-processamento de texto)
  - Descrição: executa 05_pre_processamento.py para gerar sentimentos brutos e/pre-processados.
  - Comando:
    run_pipeline.cmd textprep

- Sentiment
  - Descrição: executa 06_sentiment_analysis.py para gerar o sentimento (Original e Pré-processado).
  - Comando:
    run_pipeline.cmd sentiment

- Correlation
  - Descrição: executa 07_correlation_analysis.py para correlações e visualizações.
  - Comando:
    run_pipeline.cmd correlation

- All (pipeline completo)
  - Descrição: roda todas as etapas na sequência.
  - Comando:
    run_pipeline.cmd all

## 5) Saídas esperadas

- dados_completos.csv (pipeline_output/07_correlation)
- estatisticas_correlacao.txt (pipeline_output/07_correlation)
- scatter_sentimento_vs_variacao_d+1.png (pipeline_output/07_correlation)
- heatmap_correlacoes.png (pipeline_output/07_correlation)
- barras_comparacao_correlacoes.png (pipeline_output/07_correlation)
- boxplot_sentimento_por_empresa.png (pipeline_output/07_correlation)

Outras saídas intermediárias ficam nos diretórios:
- pipeline_output/01_03
- pipeline_output/04_fetch
- pipeline_output/05_pre
- pipeline_output/06_sentiment

## 6) Observações importantes
- O passo setup instala dependências pesadas (inclui PyTorch/Transformers). Em redes restritas, ajuste as dependências conforme necessário.
- O script assume a presença de scripts Python correspondentes nos caminhos esperados (por exemplo, 01_fetch_raw.py, 02_process_raw.py, etc.). Verifique se os nomes e caminhos estão corretos no seu repositório.
- Em ambientes diferentes (PowerShell, Linux), este Readme foca no uso via CMD no Windows.
- Se já tiver o ambiente configurado, você pode pular o passo setup e ir direto para as etapas desejadas.

## 7) Dicas úteis
- Se ocorrerem erros de permissionamento, abra o CMD como Administrador.
- Caso haja falha de rede durante a instalação, rode o setup novamente.
- Para reexecuções, você pode rodar etapas específicas sem reexecutar as já concluídas (desde que os outputs existam).

## 8) Observações finais
- Adapte caminhos e nomes de scripts conforme necessário para o seu repositório.
- Considere manter este README atualizado conforme alterações no pipeline.