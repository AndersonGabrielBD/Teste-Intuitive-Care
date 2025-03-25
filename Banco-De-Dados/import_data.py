import psycopg2
import pandas as pd

# Conectar ao banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname="teste1",  # Substitua pelo nome do seu banco de dados
    user="postgre",  # Substitua pelo seu usuário do PostgreSQL
    password="and123",  # Substitua pela sua senha do PostgreSQL
    host="localhost",  # Se estiver usando o localhost, não altere
    port="5432", # Porta padrão do PostgreSQL
    client_encoding='UTF8'  # Adicionado para garantir a codificação correta

)

cur = conn.cursor()

# Criar a tabela "demonstrativos_contabeis" se não existir
create_table_query = """
CREATE TABLE IF NOT EXISTS demonstrativos_contabeis (
    data DATE,
    registro_ans VARCHAR(20),
    cd_conta_contabil VARCHAR(20),
    descricao TEXT,
    vl_saldo_inicial NUMERIC,
    vl_saldo_final NUMERIC
);
"""
cur.execute(create_table_query)
conn.commit()

# Carregar o arquivo CSV para um DataFrame
df = pd.read_csv('C:\\Users\\gaabr\\Desktop\\arquivos\\1T2023.csv', delimiter=';')

# Limpeza de dados: substituir vírgulas por pontos e converter para float
df['vl_saldo_inicial'] = df['vl_saldo_inicial'].str.replace(',', '.').astype(float)
df['vl_saldo_final'] = df['vl_saldo_final'].str.replace(',', '.').astype(float)

# Inserir os dados na tabela "demonstrativos_contabeis"
for index, row in df.iterrows():
    insert_query = """
    INSERT INTO demonstrativos_contabeis (data, registro_ans, cd_conta_contabil, descricao, vl_saldo_inicial, vl_saldo_final)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cur.execute(insert_query, (
        row['data'], 
        row['registro_ans'], 
        row['cd_conta_contabil'], 
        row['descricao'], 
        row['vl_saldo_inicial'], 
        row['vl_saldo_final']
    ))

# Confirmar a inserção
conn.commit()

# Consultar os primeiros 10 registros para verificar se os dados foram carregados corretamente
cur.execute("SELECT * FROM demonstrativos_contabeis LIMIT 10;")
rows = cur.fetchall()

# Imprimir os dados inseridos
for row in rows:
    print(row)

# Fechar a conexão
cur.close()
conn.close()
