CREATE TABLE operadoras (
    registro_ans VARCHAR(20) PRIMARY KEY,
    cnpj VARCHAR(18),
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
    ddd VARCHAR(4),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    endereco_eletronico VARCHAR(100),
    representante VARCHAR(255),
    cargo_representante VARCHAR(100),
    regiao_de_comercializacao VARCHAR(100),
    data_registro_ans DATE
);


-- Tabela de demonstrações contábeis
CREATE TABLE demonstrativos_contabeis (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    registro_ans VARCHAR(20) NOT NULL,
    cd_conta_contabil VARCHAR(50),
    descricao VARCHAR(255),
    vl_saldo_inicial DECIMAL(15,2),
    vl_saldo_final DECIMAL(15,2),
    final DECIMAL(15,2),
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);
