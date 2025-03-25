WITH ultimo_ano AS (
    SELECT MAX(data) AS ultima_data FROM demonstrativos_contabeis
)
SELECT o.nome_fantasia, SUM(d.final) AS total_despesas
FROM demonstrativos_contabeis d
JOIN operadoras o ON d.registro_ans = o.registro_ans
WHERE d.descricao = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
  AND d.data >= (SELECT ultima_data - INTERVAL '1 YEAR' FROM ultimo_ano)
GROUP BY o.nome_fantasia
ORDER BY total_despesas DESC
LIMIT 10;
