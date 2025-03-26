Visão Geral
Este sistema realiza a importação e análise de dados da Agência Nacional de Saúde Suplementar (ANS) para um banco de dados PostgreSQL, incluindo:

-Criação automática do banco de dados e tabelas

-Importação de dados cadastrais de operadoras

-Processamento de demonstrações contábeis

-Análises estratégicas sobre despesas médicas

Pré-requisitos

-PostgreSQL 10+ instalado e rodando

-Python 3.10+

Para executar: 

Certifique que as bibliotecas python estão instaladas na pasta raiz do projeto:
pip install pandas psycopg2-binary

Modifique as informações da conexão do banco no código para as informações do seu banco local. 

OBS: É preciso mudar na conexão do começo e na do fim do arquivo "import_data.py"

no terminal dentro do diretorio ./Banco_De_Dados/data:

Execute: python import_data.py


Estrutura do Código:
1. Configuração Inicial
Define parâmetros de conexão com o PostgreSQL

Implementa função create_connection() para gerenciar conexões

Configura sistema de logging para registro de atividades

2. Setup do Banco de Dados
-Cria o banco ans_db se não existir

Define duas tabelas principais:

-operadoras: Dados cadastrais das operadoras

-demonstracoes_contabeis: Dados financeiros trimestrais

3. Importação de Dados
Para Operadoras:
Processa arquivo Relatorio_cadop.csv

Detecta automaticamente estrutura do arquivo (20 ou 21 colunas)

Converte formatos de data

Insere dados com tratamento de conflitos (UPSERT)

Para Demonstrações Contábeis:
Processa arquivos trimestrais (ex: 1T2023.csv, 2T2023.csv)

Extrai automaticamente período de competência do nome do arquivo

Padroniza nomes de colunas

Converte valores numéricos (tratando separadores decimais)

Usa COPY para alta performance na importação

4. Análise de Dados
Identifica as 10 operadoras com maiores despesas em:

Último trimestre disponível

Último ano disponível

Filtra por categorias específicas de despesas médicas

Como Executar

Configure o arquivo db_config com seus dados de acesso ao PostgreSQL

tenha os arquivos CSV na mesma pasta do script:

Relatorio_cadop.csv (dados cadastrais)

Arquivos trimestrais (ex: 1T2023.csv, 2T2023.csv, etc.)

Execute o script:

-python import_data.py

🔍 Saída Esperada
Criação do banco de dados e tabelas

Importação dos dados cadastrais

Processamento dos arquivos contábeis

Relatório analítico com:

Top 10 operadoras com maiores despesas no último trimestre

Top 10 operadoras com maiores despesas no último ano

 Observações Importantes
Verifique os caminhos dos arquivos CSV no código

Ajuste as credenciais do PostgreSQL no bloco db_config

Para grandes volumes de dados, a execução pode demorar 

Logs detalhados são gerados em importacao_demonstracoes.log

  Exemplo de Análise

=== TOP 10 NO ÚLTIMO TRIMESTRE ===
1. OPERADORA SAUDE LTDA                      R$   15,432,647.23 (em 5 contas)
2. PLANO DE SAUDE NACIONAL S.A.              R$   12,876,123.45 (em 3 contas)
...

=== TOP 10 NO ÚLTIMO ANO ===
1. OPERADORA SAUDE LTDA                      R$   58,765,432.10 (em 8 contas, 4 trimestres)
2. PLANO DE SAUDE NACIONAL S.A.              R$   45,678,901.23 (em 6 contas, 4 trimestres)
...

Melhorias Implementadas

Processamento em chunks para arquivos grandes

Tratamento robusto de erros e logging

Detecção automática de encoding

Conversão segura de tipos de dados

Índices para otimização de consultas

