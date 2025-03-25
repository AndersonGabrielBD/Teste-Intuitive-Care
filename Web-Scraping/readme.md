Descrição
Este módulo realiza o download assíncrono de arquivos PDF dos anexos disponíveis no portal da ANS (Agência Nacional de Saúde Suplementar) e os compacta em um arquivo ZIP.

Requisitos do Sistema
Python 3.8 ou superior

Bibliotecas Python necessárias: pip install aiohttp beautifulsoup4 tqdm aiofiles

pip install aiohttp beautifulsoup4 tqdm aiofiles

Execute o script principal com o comando:
python scraper.py

Funcionalidades
Download simultâneo de múltiplos arquivos PDF (até 20 conexões simultâneas)

Barra de progresso para acompanhamento dos downloads

Compactação automática dos arquivos baixados em formato ZIP

Verificação de arquivos já existentes para evitar downloads redundantes


Configuração
É possível ajustar os parâmetros na classe ANSDownloader:

timeout: Tempo máximo de espera por download (padrão: 120 segundos)

chunk_size: Tamanho dos blocos de download (padrão: 64KB)

max_connections: Número máximo de conexões simultâneas (padrão: 20)

Tratamento de Erros
O script inclui tratamento para:
-Falhas de conexão
-Timeouts
-Arquivos não encontrados
-Problemas de escrita em disco

Saída Esperada
O script irá:

Exibir o progresso dos downloads via barra de progresso

Informar o número de arquivos encontrados e baixados com sucesso

Criar um arquivo ZIP contendo todos os PDFs baixados

Reportar o caminho do arquivo ZIP gerado

Observações
Verifique sua conexão com a internet antes de executar
O script requer permissão de escrita no diretório de saída
Arquivos com o mesmo nome serão sobrescritos

