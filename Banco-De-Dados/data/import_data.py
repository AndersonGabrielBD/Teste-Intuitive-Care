import os
import pandas as pd
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from datetime import datetime
from io import StringIO
import logging
import sys
# Configurações do banco de dados PostgreSQL
db_config = {
    'host': 'localhost',
    'user': 'postgres', #nome padrao do postgree mas se for o caso substituir pelo seu 
    'password': 'and123', #substituir pela senha colocada quando baixou o postgree
    'database': 'ans_db', #o nome do banco, mas pode escolher se preferir
    'port': '5432' #porta padrao do postgree
}

def create_connection():
    try:
        connection = psycopg2.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            port=db_config['port'],
            cursor_factory=psycopg2.extras.DictCursor
        )
        return connection
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def setup_database():
    connection = None
    try:
        temp_conn = psycopg2.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port']
        )
        temp_conn.autocommit = True
        with temp_conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_config['database'],))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_config['database']))
                )
                print("Banco de dados criado com sucesso.")
        
        temp_conn.close()

        connection = create_connection()
        if connection is None:
            return
        
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS operadoras (
                registro_ans VARCHAR(20) PRIMARY KEY,
                cnpj VARCHAR(20),
                razao_social VARCHAR(255),
                nome_fantasia VARCHAR(255),
                modalidade VARCHAR(100),
                logradouro VARCHAR(255),
                numero VARCHAR(20),
                complemento VARCHAR(100),
                bairro VARCHAR(100),
                cidade VARCHAR(100),
                uf VARCHAR(2),
                cep VARCHAR(10),
                ddd VARCHAR(5),
                telefone VARCHAR(20),
                fax VARCHAR(20),
                Endereco_eletronico VARCHAR(100),
                representante VARCHAR(100),
                cargo_representante VARCHAR(100),
                regiao_decomercializacao VARCHAR(10),
                data_registro_ans DATE
            )
            """)
            
            cursor.execute("""
             DROP TABLE IF EXISTS demonstracoes_contabeis;
             CREATE TABLE demonstracoes_contabeis (
             id SERIAL PRIMARY KEY,
             registro_ans VARCHAR(20),
             competencia DATE,
             conta_contabil VARCHAR(100),
             descricao VARCHAR(255),
             vl_saldo_inicial DECIMAL(20, 2),
             vl_saldo_final DECIMAL(20, 2),
             FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
             ON DELETE CASCADE
             ON UPDATE CASCADE
            )
            """)
            
            connection.commit()
            print("Tabelas criadas com sucesso.")
            
    except psycopg2.Error as e:
        print(f"Erro ao configurar banco de dados: {e}")
    finally:
        if connection:
            connection.close()

def import_operadoras():
    connection = None
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "Relatorio_cadop.csv")
        
        if not os.path.exists(file_path):
            print(f"Erro: Arquivo não encontrado em {file_path}")
            return
        
        print(f"Lendo arquivo: {file_path}")
        df = pd.read_csv(file_path, sep=';', encoding='utf-8', dtype=str)
        
        print(f"O arquivo tem {len(df.columns)} colunas")
        
        if len(df.columns) == 20:
            df.columns = [
                'registro_ans', 'cnpj', 'razao_social', 'nome_fantasia', 'modalidade',
                'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'cep',
                'ddd', 'telefone', 'fax', 'endereco_eletronico', 'representante', 'cargo_representante','regiao_de_comercializacao',
                'data_registro_ans'
            ]
        elif len(df.columns) == 21:
            df.columns = [
                'registro_ans', 'cnpj', 'razao_social', 'nome_fantasia', 'modalidade',
                'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'cep',
                'ddd', 'telefone', 'fax', 'endereco_eletronico', 'representante', 'cargo_representante', 'regiao_de_comercializacao',
                'data_registro_ans', 'outra_coluna'
            ]
        else:
            print(f"Estrutura inesperada do arquivo: {len(df.columns)} colunas")
            return
        
        connection = create_connection()
        if connection is None:
            return
        
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE operadoras CASCADE;")
            
            total = len(df)
            print(f"Importando {total} registros...")
            
            for i, row in df.iterrows():
                row = row.where(pd.notnull(row), None)
                
                data_registro = None
                if row['data_registro_ans']:
                    try:
                        data_registro = datetime.strptime(row['data_registro_ans'], '%d/%m/%Y').date()
                    except ValueError:
                        pass
                
                cursor.execute("""
                INSERT INTO operadoras (
                    registro_ans, cnpj, razao_social, nome_fantasia, modalidade,
                    logradouro, numero, complemento, bairro, cidade, uf, cep,
                    ddd, telefone, fax, endereco_eletronico, representante, cargo_representante, regiao_de_comercializacao,
                    data_registro_ans
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (registro_ans) DO UPDATE SET
                    cnpj = EXCLUDED.cnpj,
                    razao_social = EXCLUDED.razao_social,
                    nome_fantasia = EXCLUDED.nome_fantasia,
                    modalidade = EXCLUDED.modalidade,
                    logradouro = EXCLUDED.logradouro,
                    numero = EXCLUDED.numero,
                    complemento = EXCLUDED.complemento,
                    bairro = EXCLUDED.bairro,
                    cidade = EXCLUDED.cidade,
                    uf = EXCLUDED.uf,
                    cep = EXCLUDED.cep,
                    ddd = EXCLUDED.ddd,
                    telefone = EXCLUDED.telefone,
                    fax = EXCLUDED.fax,
                    endereco_eletronico = EXCLUDED.endereco_eletronico,
                    representante = EXCLUDED.representante,
                    cargo_representante = EXCLUDED.cargo_representante,
                    regiao_de_comercializacao= EXCLUDED.regiao_de_comercializacao,
                    data_registro_ans = EXCLUDED.data_registro_ans
                """, (
                    row['registro_ans'], row['cnpj'], row['razao_social'], row['nome_fantasia'], row['modalidade'],
                    row['logradouro'], row['numero'], row['complemento'], row['bairro'], row['cidade'], row['uf'], row['cep'],
                    row['ddd'], row['telefone'], row['fax'], row['endereco_eletronico'], row['representante'], row['cargo_representante'],  row['regiao_de_comercializacao'],
                    data_registro
                ))
                
                if i % 100 == 0:
                    print(f"Progresso: {i+1}/{total} registros processados")
            
            connection.commit()
            print(f"Dados das operadoras importados com sucesso. Total: {total} registros.")
            
    except Exception as e:
        print(f"Erro ao importar dados das operadoras: {e}")
    finally:
        if connection:
            connection.close()



# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('importacao_demonstracoes.log'),
        logging.StreamHandler()
    ]
)

def import_demonstracoes_contabeis():
    connection = None
    try:
        # Lista de arquivos a processar
        arquivos = [f"{trimestre}T{ano}.csv" 
                   for ano in [2023, 2024] 
                   for trimestre in range(1, 5)]
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        connection = create_connection()
        if connection is None:
            logging.error("Falha ao conectar ao banco de dados")
            return

        with connection.cursor() as cursor:
            # ETAPA 1: Identificar todas as operadoras necessárias
            logging.info("Identificando operadoras necessárias...")
            all_operadoras = set()
            
            for arquivo in arquivos:
                file_path = os.path.join(script_dir, arquivo)
                if not os.path.exists(file_path):
                    logging.warning(f"Arquivo {arquivo} não encontrado")
                    continue
                
                try:
                    # Leitura eficiente apenas da coluna REG_ANS
                    for chunk in pd.read_csv(file_path, sep=';', encoding='utf-8', 
                                           dtype={'REG_ANS': str}, chunksize=10000):
                        all_operadoras.update(chunk['REG_ANS'].dropna().unique())
                except Exception as e:
                    logging.error(f"Erro ao processar {arquivo}: {str(e)}")
                    continue
            
            logging.info(f"Total de operadoras identificadas: {len(all_operadoras)}")

            # ETAPA 2: Cadastrar operadoras faltantes
            if all_operadoras:
                logging.info("Verificando operadoras faltantes...")
                
                # Consulta eficiente para operadoras existentes
                cursor.execute("SELECT registro_ans FROM operadoras WHERE registro_ans = ANY(%s)", 
                             (list(all_operadoras),))
                existing_ops = {r[0] for r in cursor.fetchall()}
                new_ops = all_operadoras - existing_ops
                
                if new_ops:
                    logging.info(f"Encontradas {len(new_ops)} novas operadoras para cadastrar")
                    
                    # Inserção em lote eficiente
                    values = [(op, f"Operadora {op} (cadastro automático)") for op in new_ops]
                    args = ','.join(cursor.mogrify("(%s,%s)", v).decode('utf-8') for v in values)
                    
                    cursor.execute(
                        f"INSERT INTO operadoras (registro_ans, razao_social) VALUES {args} "
                        "ON CONFLICT (registro_ans) DO NOTHING"
                    )
                    connection.commit()
                    logging.info("Novas operadoras cadastradas com sucesso")

            # ETAPA 3: Processar arquivos de demonstrações
            logging.info("Iniciando importação dos arquivos...")
            
            # Preparar tabela
            cursor.execute("""
            DROP INDEX IF EXISTS idx_demonstracoes_registro_ans;
            TRUNCATE TABLE demonstracoes_contabeis;
            """)
            connection.commit()

            total_registros = 0
            batch_size = 5000

            for arquivo in arquivos:
                file_path = os.path.join(script_dir, arquivo)
                if not os.path.exists(file_path):
                    continue
                
                try:
                    # Extrair competência do nome do arquivo
                    trimestre, ano = arquivo.split('T')
                    ano = ano.replace('.csv', '')
                    mes = int(trimestre) * 3
                    competencia = datetime(int(ano), mes, 1).date()
                    logging.info(f"Processando {arquivo} - Competência: {competencia}")
                except Exception as e:
                    logging.error(f"Erro ao extrair data de {arquivo}: {str(e)}")
                    continue

                # Processar em chunks
                for chunk in pd.read_csv(file_path, sep=';', encoding='utf-8', 
                                       dtype=str, chunksize=batch_size):
                    try:
                        # Padronizar nomes de colunas
                        chunk.columns = ['DATA', 'REG_ANS', 'CD_CONTA_CONTABIL', 
                                       'DESCRICAO', 'VL_SALDO_INICIAL', 'VL_SALDO_FINAL']
                        
                        # Converter valores numéricos
                        for col in ['VL_SALDO_INICIAL', 'VL_SALDO_FINAL']:
                            chunk[col] = pd.to_numeric(
                                chunk[col].str.replace(',', '.').str.replace('[^\d.]', '', regex=True),
                                errors='coerce'
                            )
                        
                        # Remover linhas inválidas
                        chunk = chunk.dropna(subset=['VL_SALDO_FINAL', 'REG_ANS'])
                        
                        if len(chunk) == 0:
                            continue
                        
                        # Adicionar competência
                        chunk['COMPETENCIA'] = competencia.strftime('%Y-%m-%d')
                        
                        # Preparar dados para COPY
                        output = StringIO()
                        chunk.to_csv(
                            output, 
                            sep='\t', 
                            header=False, 
                            index=False,
                            columns=['REG_ANS', 'CD_CONTA_CONTABIL', 'DESCRICAO', 
                                    'VL_SALDO_INICIAL', 'VL_SALDO_FINAL', 'COMPETENCIA']
                        )
                        output.seek(0)
                        
                        # Executar COPY
                        cursor.copy_expert(
                            """
                            COPY demonstracoes_contabeis (
                                registro_ans, conta_contabil, descricao,
                                vl_saldo_inicial, vl_saldo_final, competencia
                            ) FROM STDIN WITH (FORMAT CSV, DELIMITER '\t', NULL '')
                            """,
                            output
                        )
                        connection.commit()
                        
                        total_registros += len(chunk)
                        logging.info(f"  Lote de {len(chunk)} registros importado")
                        
                    except Exception as e:
                        connection.rollback()
                        logging.error(f"Erro no lote: {str(e)}")
                        continue

            # ETAPA 4: Finalização
            logging.info("Reconstruindo índices...")
            cursor.execute("""
            CREATE INDEX idx_demonstracoes_registro_ans ON demonstracoes_contabeis(registro_ans);
            CREATE INDEX idx_demonstracoes_competencia ON demonstracoes_contabeis(competencia);
            """)
            connection.commit()
            
            logging.info(f"Importação concluída! Total de registros: {total_registros}")
            
    except Exception as e:
        logging.error(f"ERRO GRAVE: {str(e)}", exc_info=True)
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()
        logging.info("Conexão com o banco encerrada")


def obter_maiores_despesas(connection):

    try:
        with connection.cursor() as cursor:
            print("\nExecutando queries analíticas...\n")
            
            # Verifica se existem dados nas tabelas
            cursor.execute("SELECT COUNT(*) FROM demonstracoes_contabeis")
            total_registros = cursor.fetchone()[0]
            print(f"Total de registros contábeis encontrados: {total_registros}")
            
            if total_registros == 0:
                print("Nenhum registro encontrado na tabela demonstracoes_contabeis")
                return False
            
            # Query 1: Último trimestre 
            cursor.execute("""
            WITH descricoes_relevantes AS (
                SELECT DISTINCT conta_contabil 
                FROM demonstracoes_contabeis 
                WHERE descricao ILIKE '%%EVENTOS/%%SINISTROS%%ASSISTÊNCIA%%SAÚDE%%'
                LIMIT 10
            ),
            ultimo_trimestre AS (
                SELECT DATE_TRUNC('quarter', MAX(competencia)) AS ultimo_trimestre
                FROM demonstracoes_contabeis
            )
            SELECT 
                o.razao_social AS operadora,
                SUM(d.vl_saldo_final) AS total_despesas,
                COUNT(DISTINCT d.conta_contabil) AS qtd_contas
            FROM demonstracoes_contabeis d
            JOIN operadoras o ON d.registro_ans = o.registro_ans
            JOIN descricoes_relevantes dr ON d.conta_contabil = dr.conta_contabil
            CROSS JOIN ultimo_trimestre ut
            WHERE DATE_TRUNC('quarter', d.competencia) = ut.ultimo_trimestre
            GROUP BY o.razao_social
            ORDER BY total_despesas DESC
            LIMIT 10;
            """)
            top_trimestre = cursor.fetchall()

            # Query 2: Último ano 
            cursor.execute("""
            WITH descricoes_relevantes AS (
                SELECT DISTINCT conta_contabil 
                FROM demonstracoes_contabeis 
                WHERE descricao ILIKE '%%EVENTOS/%%SINISTROS%%ASSISTÊNCIA%%SAÚDE%%'
                LIMIT 10
            ),
            ultimo_ano AS (
                SELECT DATE_TRUNC('year', MAX(competencia)) AS ultimo_ano
                FROM demonstracoes_contabeis
            )
            SELECT 
                o.razao_social AS operadora,
                SUM(d.vl_saldo_final) AS total_despesas,
                COUNT(DISTINCT d.conta_contabil) AS qtd_contas,
                COUNT(DISTINCT DATE_TRUNC('quarter', d.competencia)) AS trimestres
            FROM demonstracoes_contabeis d
            JOIN operadoras o ON d.registro_ans = o.registro_ans
            JOIN descricoes_relevantes dr ON d.conta_contabil = dr.conta_contabil
            CROSS JOIN ultimo_ano ua
            WHERE DATE_TRUNC('year', d.competencia) = ua.ultimo_ano
            GROUP BY o.razao_social
            ORDER BY total_despesas DESC
            LIMIT 10;
            """)
            top_ano = cursor.fetchall()

            # Resultados formatados
            print("\n=== TOP 10 NO ÚLTIMO TRIMESTRE ===")
            if top_trimestre:
                for idx, (operadora, valor, contas) in enumerate(top_trimestre, 1):
                    print(f"{idx}. {operadora[:50]:<50} R$ {valor:>15,.2f} (em {contas} contas)")
            else:
                print("Nenhum resultado encontrado para o último trimestre")

            print("\n=== TOP 10 NO ÚLTIMO ANO ===")
            if top_ano:
                for idx, (operadora, valor, contas, trimestres) in enumerate(top_ano, 1):
                    print(f"{idx}. {operadora[:50]:<50} R$ {valor:>15,.2f} (em {contas} contas, {trimestres} trimestres)")
            else:
                print("Nenhum resultado encontrado para o último ano")

            return True

    except Exception as e:
        print(f"\nERRO: {e}\n", file=sys.stderr)
        return False


    
if __name__ == "__main__":
    print("Iniciando processo de importação...")
    
    print("\nCriando banco de dados e tabelas...")
    setup_database()
    
    print("\nImportando dados das operadoras...")
    import_operadoras()
    
    print("\nImportando demonstrações contábeis...")
    import_demonstracoes_contabeis()
    try:
        # Configuração da conexão 
        conn = psycopg2.connect(
            dbname="ans_db", #o nome do banco, mas pode escolher se preferir
            user="postgres", #user padrao do postgree mas se for o caso substituir pelo seu 
            password="and123",  #substituir pela senha colocada quando baixou o postgree
            host="localhost", 
            port="5432" #porta padrao do postgree
        )
        
        # Executar a análise
        sucesso = obter_maiores_despesas(conn)
        
        if sucesso:
            print("\nProcesso concluído com sucesso!")
        else:
            print("\nProcesso concluído com avisos.", file=sys.stderr)
            
    except psycopg2.Error as e:
        print(f"\nERRO DE CONEXÃO: {e}\n", file=sys.stderr)
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()


    