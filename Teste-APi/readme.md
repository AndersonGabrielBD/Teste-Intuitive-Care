Visão Geral
Solução completa para consulta ao cadastro de operadoras de saúde da ANS, composta por:
Backend: API REST em Flask com busca textual inteligente
Frontend: Interface em Vue.js
Postman: testes do backend
Integração: Comunicação eficiente entre frontend e backend

Pré-requisitos
Backend
Python 3.10+

Pacotes Python:
pip install flask flask-cors pandas fuzzywuzzy python-Levenshtein

Frontend
Node.js 18+

npm 9+ ou yarn 1.22+

Instalação e Execução

Backend
Acesse a pasta do backend:
cd backend/

Instale as dependências: pip install flask flask-cors pandas fuzzywuzzy python-Levenshtein


Inicie o servidor:
python app.py
Servidor estará disponível em: http://localhost:5000

Frontend

Acesse a pasta do frontend:
cd frontend/

Instale as dependências:

npm install
# ou
yarn install

Inicie a aplicação:
npm run dev
# ou
yarn dev
Acesse: http://localhost:5173

🔧 Endpoints da API
GET /api/status
Verifica status do servidor

Retorno:
{
  "status": "online",
  "hora_servidor": "2023-11-20T15:30:00",
  "dados_carregados": true,
  "total_registros": 1500
}

GET /api/buscar
Busca textual por operadoras

Parâmetros:

q: termo de busca (obrigatório)

limit: limite de resultados (padrão: 20)

uf: filtrar por UF

modalidade: filtrar por modalidade

GET /api/detalhes/<registro_ans>
Retorna detalhes completos de uma operadora


Funcionalidades:

Busca inteligente: Combina correspondência exata e fuzzy search

Filtros: Por UF e modalidade

Paginação: Controle de limite de resultados

Tratamento de dados: Conversão automática de encoding

Solução de Problemas

CSV não encontrado: Verifique o caminho em CSV_PATH

Problemas de encoding: O sistema tenta automaticamente 4 encodings diferentes

Logs detalhados: Verifique o console para mensagens de erro

Dados de Exemplo
A API espera um CSV com pelo menos estas colunas (nomes alternativos são aceitos):

Registro_ANS

Razao_Social

CNPJ

Modalidade

UF

Cidade

Observações Importantes:

O servidor deve estar rodando antes de acessar o frontend

Para produção, configure:

Variáveis de ambiente

CORS adequadamente

Logging em arquivo

O arquivo CSV deve usar ; como delimitador

