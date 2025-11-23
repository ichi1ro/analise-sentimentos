# Universidade Estadual de Maringá
# Departamento de Informática

## Trabalho Prático 2 de Introdução à Inteligência Artificial

## Objetivo Geral

O trabalho tem como foco a análise de sentimentos de notícias financeiras relacionadas a empresas da Bolsa de Valores brasileira (B3), utilizando técnicas de Processamento de Linguagem Natural (PLN). Além disso, será analisada a correlação entre o sentimento das notícias e a variação dos preços das ações dessas empresas. Cada 2 equipes (no máximo) deverá escolher um setor diferente e analisar as empresas que sejam deste setor (lista de setores no ANEXO A, postar a escolha do setor no classroom).

## Modalidade

- Trabalho individual ou em grupo, com no máximo **4 integrantes**.
- Cada aluno deverá analisar uma empresa diferente, de forma que, se a equipe tiver 3 integrantes, serão analisadas 3 empresas (15 notícias de cada empresa).

## Metodologia Detalhada

### 1. Coleta de Dados Financeiros e Notícias

#### Seleção de Empresas:
- Cada aluno deve escolher uma empresa listada na **B3** que possua dados financeiros disponíveis no Yahoo Finance.
- Exemplos de empresas: Petrobras (PETR4), Magazine Luiza (MGLU3), Itaú Unibanco (ITUB4), Vale (VALE3).

#### Coleta de Notícias Financeiras:
- Selecionar um portal de notícias financeiras confiável como:
  - Yahoo Finance
  - Bloomberg
  - Reuters
  - Wall Street Journal
  - InfoMoney
- Utilizar **web scraping** ou APIs, dependendo da disponibilidade do portal, para extrair notícias sobre as empresas selecionadas.
- Armazenar as informações relevantes de cada notícia:
  - Título
  - Data de publicação
  - Corpo do texto
  - URL (caso aplicável)

### 2. Análise de Dados Financeiros

#### Coleta de Preços:
- Utilizar a biblioteca `yfinance` para obter dados históricos dos preços das ações das empresas selecionadas.
- Armazenar informações importantes:
  - Preço de abertura e fechamento diário.
  - Variação percentual diária.

#### Relacionamento Temporal:
- Definir um intervalo de análise que inclui:
  - O **dia da publicação** da notícia.
  - **1 dia antes e 1 dia depois**.
  - **2 dias antes e 2 dias depois**.
- Observar a variação de preços nos dias em questão.

### 3. Pré-Processamento das Notícias

O pré-processamento das notícias é essencial para melhorar a precisão da análise de sentimentos. Os seguintes passos devem ser seguidos:

- **Tokenização**:
  - Dividir o texto em unidades menores chamadas tokens (geralmente palavras).
- **Caixa Baixa**:
  - Converter todas as palavras para minúsculas para uniformizar o texto.
- **Remoção de Stop-Words**:
  - Eliminar palavras comuns sem significado importante para a análise (ex.: "de", "a", "que").
- **Lematização ou Stemming**:
  - Reduzir palavras à sua forma base (ex.: "correndo" → "correr").
- **Remoção de Pontuação e Caracteres Especiais**:
  - Limpar o texto, retirando pontuações e caracteres que não influenciam a análise de sentimento.

### 4. Análise de Sentimentos

- **Escolha de um modelo** para realizar a análise de sentimentos:
  - **Bag-of-Words** ou **N-Grama** para abordagem tradicional.
  - **Transformers** (e.g., BERT ou DistilBERT) para abordagens mais avançadas.
- **Implementação do Modelo**:
  - Criar um modelo que analise as notícias e atribua uma **pontuação de sentimento** que pode variar de negativa a positiva (e.g., -10 a +10).
  - Utilizar bibliotecas de PLN como **NLTK**, **spaCy** ou **Transformers**.
- **Comparação dos Resultados**:
  - Avaliar o impacto do uso de técnicas de pré-processamento na análise.
  - Comparar resultados com e sem pré-processamento.

### 5. Correlação entre Sentimentos e Variação dos Preços

#### Correlação Temporal:
- Calcular a correlação entre o sentimento da notícia e a variação dos preços no mesmo dia e em dias anteriores e posteriores.
- Utilizar o **coeficiente de correlação de Pearson** para avaliar a relação entre os sentimentos expressos nas notícias e a variação dos preços.

#### Gráficos e Visualizações:
- Gerar gráficos para ilustrar a correlação:
  - Sentimento x Variação de Preço no dia da notícia.
  - Sentimento x Variação de Preço **1 dia antes**.
  - Sentimento x Variação de Preço **1 dia depois**.
  - Sentimento x Variação de Preço **2 dias antes e 2 dias depois**.

## Entrega do Trabalho

### Apresentação de Slides

Os slides devem cobrir:

- Introdução ao Problema
- Rápida fundamentação teórica
- Metodologia Utilizada
- Análise de Resultados com gráficos.
- Conclusões e discussão dos resultados.
- Tecnologias Utilizadas (ambiente de desenvolvimento, bibliotecas e plataformas).
- Trechos de Código ilustrando implementações-chave.
- Referências Bibliográficas

## Tecnologias e Ferramentas Recomendadas

- **Python** como linguagem principal.
- **Ambiente**: Google Colab ou Jupyter Notebook.
- **Bibliotecas**:
  - **Pandas** e **NumPy** para manipulação e análise de dados.
  - **Matplotlib** e **Seaborn** para visualização de gráficos.
  - **NLTK**, **spaCy** ou **Transformers** para PLN.
  - **BeautifulSoup** e **Selenium** para web scraping.
  - **yfinance** para coleta de dados financeiros.

## Critérios de Avaliação

- **Completude**: Se todas as etapas especificadas foram realizadas.
- **Correção**: A precisão na análise dos sentimentos e correlação.
- **Qualidade da Implementação**: Código funcional, documentado e de fácil entendimento.
- **Originalidade**: Soluções inovadoras e abordagens não convencionais.
- **Apresentação**: Clareza nos relatórios e slides, com gráficos e tabelas que suportam as conclusões.
- **Entrega no Prazo**: Trabalhos entregues fora do prazo terão penalizações na nota final.

---

## ANEXO A

### Energia

- **Descrição**: Empresas que atuam na geração, distribuição, comercialização e transporte de energia elétrica, gás e derivados de petróleo.
- **Exemplos de Empresas**:
  - Petrobras (PETR4)
  - Eletrobras (ELET3, ELET6)
  - Eneva (ENEV3)
  - Engie Brasil (EGIE3)

### Financeiro e Outros

- **Descrição**: Empresas que operam no setor bancário, financeiro, seguros, investimentos e holdings.
- **Exemplos de Empresas**:
  - Itaú Unibanco (ITUB4)
  - Banco do Brasil (BBAS3)
  - Bradesco (BBDC4)
  - BTG Pactual (BPAC11)

### Consumo Cíclico

- **Descrição**: Empresas relacionadas ao consumo não essencial, como varejo, automóveis, vestuário e eletrodomésticos.
- **Exemplos de Empresas**:
  - Magazine Luiza (MGLU3)
  - Via Varejo (VIIA3)
  - Lojas Americanas (AMER3)
  - Localiza (RENT3)

### Consumo Não Cíclico

- **Descrição**: Empresas focadas em produtos essenciais e de consumo constante, como alimentos, bebidas e higiene.
- **Exemplos de Empresas**:
  - Ambev (ABEV3)
  - Carrefour Brasil (CRFB3)
  - BRF (BRFS3)
  - JBS (JBSS3)

### Materiais Básicos

- **Descrição**: Empresas que atuam na produção de matérias-primas, mineração, metalurgia, siderurgia e produtos químicos.
- **Exemplos de Empresas**:
  - Vale (VALE3)
  - Gerdau (GGBR4)
  - CSN (CSNA3)
  - Braskem (BRKM5)

### Saúde

- **Descrição**: Empresas do setor de saúde, incluindo hospitais, laboratórios, planos de saúde e fabricantes de produtos médicos.
- **Exemplos de Empresas**:
  - Hapvida (HAPV3)
  - Fleury (FLRY3)
  - NotreDame Intermédica (GNDI3)
  - Hypera Pharma (HYPE3)

### Tecnologia da Informação

- **Descrição**: Empresas que atuam no desenvolvimento de software, serviços de TI e hardware.
- **Exemplos de Empresas**:
  - TOTVS (TOTS3)
  - Positivo Tecnologia (POSI3)
  - Locaweb (LWSA3)
  - Sinqia (SQIA3)

### Utilidade Pública

- **Descrição**: Empresas que oferecem serviços essenciais, como água, esgoto e distribuição de energia elétrica.
- **Exemplos de Empresas**:
  - Copel (CPLE6)
  - CESP (CESP6)
  - Sabesp (SBSP3)
  - Cemig (CMIG4)

### Comunicações

- **Descrição**: Empresas que operam no setor de telecomunicações, como telefonia fixa, móvel, internet e TV por assinatura.
- **Exemplos de Empresas**:
  - Telefônica Brasil (VIVT3)
  - Oi (OIBR3)
  - Tim Brasil (TIMS3)

### Bens Industriais

- **Descrição**: Empresas que fabricam produtos para indústrias, equipamentos de transporte, construção civil e logística.
- **Exemplos de Empresas**:
  - WEG (WEGE3)
  - Embraer (EMBR3)
  - Rumo (RAIL3)
  - CCR (CCRO3)

### Imobiliário

- **Descrição**: Empresas que atuam no setor de construção, desenvolvimento, aluguel e venda de imóveis.
- **Exemplos de Empresas**:
  - Cyrela (CYRE3)
  - MRV Engenharia (MRVE3)
  - Multiplan (MULT3)
  - JHSF (JHSF3)

### Petróleo, Gás e Biocombustíveis

- **Descrição**: Empresas que operam na extração, refino e distribuição de petróleo, gás natural e biocombustíveis.
- **Exemplos de Empresas**:
  - Petrobras (PETR4)
  - PetroRio (PRIO3)
  - Cosan (CSAN3)
  - Ultrapar (UGPA3)

### Siderurgia e Mineração

- **Descrição**: Empresas que produzem materiais metálicos e não-metálicos, como aço, ferro e outros minerais.
- **Exemplos de Empresas**:
  - Gerdau (GGBR4)
  - Usiminas (USIM5)
  - CSN (CSNA3)
  - Vale (VALE3)
