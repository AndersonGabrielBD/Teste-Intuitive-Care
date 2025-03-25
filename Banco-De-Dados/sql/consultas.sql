-- 1. Top 10 operadoras com maiores despesas hospitalares no último trimestre
WITH dados_trimestre AS (
    SELECT 
        o.nome_fantasia,
        o.uf,
        o.cidade,
        SUM(d.valor) AS total_despesas
    FROM demonstracoes_contabeis d
    JOIN operadoras o ON d.registro_ans = o.registro_ans
    WHERE d.descricao LIKE '%EVENTOS/%SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
      AND d.competencia >= DATE_SUB(CURRENT_DATE, INTERVAL 3 MONTH)
    GROUP BY o.nome_fantasia, o.uf, o.cidade
    ORDER BY total_despesas DESC
    LIMIT 10
)
SELECT 
    nome_fantasia AS "Operadora",
    CONCAT(cidade, '/', uf) AS "Localização",
    CONCAT('R$ ', FORMAT(total_despesas, 2, 'pt_BR')) AS "Despesas Trimestrais"
FROM dados_trimestre;

-- 2. Top 10 operadoras com maiores despesas hospitalares no último ano
SELECT 
    o.nome_fantasia AS "Operadora",
    o.telefone AS "Telefone",
    o.endereco_eletronico AS "E-mail",
    CONCAT('R$ ', FORMAT(SUM(d.valor), 2, 'pt_BR')) AS "Despesas Anuais"
FROM demonstracoes_contabeis d
JOIN operadoras o ON d.registro_ans = o.registro_ans
WHERE d.descricao LIKE '%EVENTOS/%SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
  AND d.competencia >= DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR)
GROUP BY o.nome_fantasia, o.telefone, o.endereco_eletronico
ORDER BY SUM(d.valor) DESC
LIMIT 10;