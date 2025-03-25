-- Importação das operadoras ativas (com todas as colunas)
COPY operadoras FROM '../Relatorio_cadop.csv'
DELIMITER ';' 
CSV HEADER;


-- Importação das demonstrações contábeis
COPY demonstracoes_contabeis(registro_ans, competencia, conta_contabil, descricao, valor)
FROM '/caminho/completo/para/demonstracoes_2023.csv'
WITH CSV HEADER DELIMITER ';' ENCODING 'LATIN1';


-- Desabilitar temporariamente a verificação de chave estrangeira
ALTER TABLE demonstrativos_contabeis DISABLE TRIGGER ALL;

-- Realizar a importação dos dados
COPY demonstrativos_contabeis (data, registro_ans, cd_conta_contabil, descricao, vl_saldo_inicial, vl_saldo_final)
FROM 'C:\\Users\\gaabr\\Desktop\\arquivos\\4T2024.csv'
DELIMITER ';'
CSV HEADER;

-- Reabilitar a verificação de chave estrangeira
ALTER TABLE demonstrativos_contabeis ENABLE TRIGGER ALL;
