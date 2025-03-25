Descrição
Este módulo realiza a extração e transformação de dados do Rol de Procedimentos da ANS (Anexo I) de um arquivo PDF para formato CSV estruturado, com posterior compactação em arquivo ZIP.

Requisitos do Sistema
Python 3.8 ou superior

Bibliotecas Python necessárias:
pip install tabula-py pandas pdfplumber concurrent-log-handler

Para executar 

1-Verifique se instalou todas as dependencias: pip install tabula-py pandas pdfplumber concurrent-log-handler

2-Certifique-se de ter o arquivo PDF Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf na pasta Web-Scraping/output/ans_pdfs/ que foi resultado do teste anterior

3-python transform_dados.py

Funcionalidades

-Extração de tabelas de PDF usando múltiplos métodos (Tabula e PDFPlumber)

-Processamento paralelo de páginas para melhor performance

-Limpeza e padronização dos dados

-Substituição automática de abreviações (OD → Seg. Odontológica, AMB → Seg. Ambulatorial)

-Compactação automática do CSV em arquivo ZIP

Configuração
Parâmetros ajustáveis no código:



# Métodos de extração:
extract_with_tabula()     # Usa a biblioteca Tabula
extract_with_pdfplumber() # Usa PDFPlumber como fallback


Tratamento de Erros
O script inclui tratamento para:

-Falhas na extração de tabelas

-Problemas de codificação de caracteres

-Arquivos de entrada ausentes

-Problemas de escrita em disco

Saída Esperada:
Arquivo CSV estruturado com os dados da tabela

Arquivo ZIP contendo o CSV

Mensagens de progresso no console

Observações:
-Requer que o PDF de entrada esteja na pasta especificada

-Verifique permissões de escrita no diretório de saída

-Arquivos existentes serão sobrescritos

-O processo pode demorar para PDFs grandes