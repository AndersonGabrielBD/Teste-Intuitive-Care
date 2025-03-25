from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzywuzzy import fuzz
import os
import logging
from datetime import datetime

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configurações
CSV_PATH = os.path.join(os.path.dirname(__file__), 'Relatorio_cadop2.csv')
df = pd.DataFrame()

# Mapeamento de colunas 
COLUNAS = {
    'registro_ans': ['Registro_ANS', 'Registro ANS', 'registro_ans'],
    'cnpj': ['CNPJ', 'cnpj'],
    'razao_social': ['Razao_Social', 'Razão Social', 'razao_social'],
    'nome_fantasia': ['Nome_Fantasia', 'Nome Fantasia', 'nome_fantasia'],
    'modalidade': ['Modalidade', 'modalidade'],
    'uf': ['UF', 'uf', 'UF'],
    'cidade': ['Cidade', 'cidade'],
    'logradouro': ['Logradouro', 'logradouro'],
    'numero': ['Número', 'numero'],
    'bairro': ['Bairro', 'bairro'],
    'telefone': ['Telefone', 'telefone'],
    'fax': ['Fax', 'fax'],
    'endereco_eletronico': ['Endereço_eletrônico', 'Email', 'endereco_eletronico']
}

def encontrar_nome_coluna(padroes, df_columns):
    for padrao in padroes:
        if padrao in df_columns:
            return padrao
    return None

def carregar_dados():
    global df
    
    try:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"Arquivo CSV não encontrado em: {CSV_PATH}")

        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
        
        for encoding in encodings:
            try:
                temp_df = pd.read_csv(CSV_PATH, delimiter=';', encoding=encoding, dtype=str)
                
                colunas_mapeadas = {}
                for col, alternativas in COLUNAS.items():
                    nome_real = encontrar_nome_coluna(alternativas, temp_df.columns)
                    if nome_real:
                        colunas_mapeadas[col] = nome_real
                
                temp_df = temp_df.rename(columns={v: k for k, v in colunas_mapeadas.items()})
                
                colunas_essenciais = ['registro_ans', 'razao_social', 'cnpj']
                if not all(col in temp_df.columns for col in colunas_essenciais):
                    raise ValueError(f"CSV não contém todas as colunas essenciais")
                
                df = temp_df.where(pd.notnull(temp_df), None)
                logging.info(f"CSV carregado com sucesso. Total de registros: {len(df)}")
                return True
                
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Não foi possível ler o CSV com nenhum encoding comum")
        
    except Exception as e:
        logging.error(f"Erro ao carregar CSV: {str(e)}")
        df = pd.DataFrame()
        return False

carregar_dados()

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "hora_servidor": datetime.now().isoformat(),
        "dados_carregados": not df.empty,
        "total_registros": len(df) if not df.empty else 0
    })

@app.route('/api/buscar', methods=['GET'])
def buscar_operadoras():
    try:
        termo = request.args.get('q', '').strip().lower()
        limite = min(int(request.args.get('limit', 20)), 100) 
        uf = request.args.get('uf', '').strip().upper()
        modalidade = request.args.get('modalidade', '').strip().lower()
        
        if not termo or df.empty:
            return jsonify([])
        
        # Pré-filtro para melhor performance
        mask = (
            df['razao_social'].str.lower().str.contains(termo, na=False) |
            df['nome_fantasia'].str.lower().str.contains(termo, na=False) |
            df['registro_ans'].str.contains(termo, na=False) |
            df['cnpj'].str.contains(termo, na=False)
        )
        if uf:
            mask &= df['uf'].str.upper() == uf
        if modalidade:
            mask &= df['modalidade'].str.lower() == modalidade
        
        filtered = df[mask].copy()
        
        # Calcula relevância apenas para os pré-filtrados
        def calcular_relevancia(row):
            scores = [
                fuzz.token_set_ratio(termo, str(row['razao_social']).lower()),
                fuzz.token_set_ratio(termo, str(row['nome_fantasia']).lower()),
                fuzz.token_set_ratio(termo, str(row['registro_ans']).lower()),
                fuzz.token_set_ratio(termo, str(row['cnpj']).lower())
            ]
            return max(scores)
        
        filtered['relevancia'] = filtered.apply(calcular_relevancia, axis=1)
        
        # Ordena e limita
        resultados = filtered.nlargest(limite, 'relevancia')
        
        # Formata a resposta
        response_data = [{
            'relevancia': row['relevancia'],
            'dados': {
                k: row[k] for k in [
                    'registro_ans', 'razao_social', 'nome_fantasia', 'cnpj',
                    'modalidade', 'uf', 'cidade', 'logradouro', 'numero',
                    'bairro', 'telefone', 'fax', 'endereco_eletronico'
                ] if k in row
            }
        } for _, row in resultados.iterrows()]
        
        return jsonify(response_data)
    
    except Exception as e:
        logging.error(f"Erro na busca: {str(e)}")
        return jsonify({'error': 'Erro interno no servidor'}), 500
@app.route('/api/detalhes/<registro_ans>', methods=['GET'])
def detalhes_operadora(registro_ans):
    try:
        if df.empty:
            logging.error("Dataframe vazio - dados não carregados")
            return jsonify({"error": "Dados não carregados"}), 503
            
        # Converter para string e remover espaços
        registro_ans = str(registro_ans).strip()
        
        # Debug: logar o valor recebido
        logging.info(f"Buscando detalhes para registro: {registro_ans}")
        
        # Verificar se o registro existe (comparação como string)
        operadora = df[df['registro_ans'].astype(str).str.strip() == registro_ans]
        
        if operadora.empty:
            logging.warning(f"Registro não encontrado: {registro_ans}")
            # Debug: listar alguns registros disponíveis
            sample_records = df['registro_ans'].astype(str).str.strip().unique()[:5]
            logging.info(f"Registros disponíveis (amostra): {sample_records}")
            return jsonify({'error': 'Operadora não encontrada', 'registro_procurado': registro_ans}), 404
        
        # Converter para dicionário e tratar valores nulos
        dados = operadora.iloc[0].replace({pd.NA: None, pd.NaT: None}).to_dict()
        
        # Debug: logar os dados encontrados
        logging.info(f"Dados encontrados para {registro_ans}: {dados.keys()}")
        
        return jsonify(dados)
    
    except Exception as e:
        logging.error(f"Erro ao buscar detalhes: {str(e)}", exc_info=True)
        return jsonify({'error': 'Erro interno no servidor', 'detalhes': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)