
-- SCRIPT: consultas.sql
-- OBJETIVO: Consultas de média/alta complexidade para o Projeto Tamar

/* CONSULTA 1: DIVISÃO RELACIONAL 
Objetivo: Listar o Nome e CPF dos Pesquisadores que já atuaram em 
resgates em TODAS as Áreas de Monitoramento do projeto.

Justificativa: Permite mapear os pesquisadores com maior mobilidade 
geográfica, fundamentais para liderar treinamentos nas diferentes 
regiões litorâneas.*/

SELECT 
    p.Nome, 
    p.CPF
FROM Pessoa p
JOIN Pesquisador pq 
    ON p.CPF = pq.CPF
WHERE NOT EXISTS (
    SELECT a.UF, a.cidade
    FROM Area_de_Monitoramento a
    WHERE NOT EXISTS (
        SELECT 1
        FROM Resgate_Encalhe r
        WHERE r.CPF_Pesq = pq.CPF
          AND r.UF = a.UF
          AND r.cidade = a.cidade
    )
);


/* CONSULTA 2: ANINHADA CORRELACIONADA (FOCO BIOLÓGICO/CONSERVAÇÃO)
Objetivo: Identificar as tartarugas e as áreas de monitoramento de 
seus ninhos que tiveram uma "taxa de eclosão" (percentual de filhotes)
SUPERIOR à taxa média de eclosão dos ninhos da MESMA ESPÉCIE.

Justificativa: Indicador crucial de sucesso reprodutivo. Permite mapear 
matrizes (fêmeas) altamente férteis ou trechos de praia com condições 
de incubação ideais. */

SELECT 
    t1.codigo_anilha AS "Código da Tartaruga",
    d1.UF AS "UF (Área de Monitoramento)",
    d1.cidade AS "Cidade (Área de Monitoramento)",
    t1.nome_cientifico AS "Espécie",
    e1.nivel_de_extincao AS "Nível de Extinção",
    n1.n_ovos AS "Total de Ovos",
    n1.n_filhotes AS "Total de Filhotes",
    ROUND((n1.n_filhotes / n1.n_ovos) * 100, 2) AS "Taxa de Eclosão (%)"
FROM Desova d1
JOIN Ninho n1 
    ON d1.codigo_estaca = n1.codigo_estaca
JOIN Tartaruga t1 
    ON d1.codigo_anilha = t1.codigo_anilha
JOIN Especie e1 
    ON e1.nome_cientifico = t1.nome_cientifico
WHERE (n1.n_filhotes / n1.n_ovos) > (
    SELECT AVG(n2.n_filhotes / n2.n_ovos)
    FROM Desova d2
    JOIN Ninho n2 
        ON d2.codigo_estaca = n2.codigo_estaca
    JOIN Tartaruga t2 
        ON d2.codigo_anilha = t2.codigo_anilha
    WHERE t2.nome_cientifico = t1.nome_cientifico
);

/* CONSULTA 3: TARTARUGAS REABILITADAS COM EVENTOS POSTERIORES
Objetivo: Identificar tartarugas que, após passarem por um processo 
de reabilitação e serem registradas como vivas em um resgate/encalhe,
continuaram participando de atividades monitoradas (pesca ou desova).

Justificativa: Permite avaliar a eficácia dos processos de reabilitação
e reinserção do projeto, comprovando que o animal retornou à natureza 
saudável e ativo (comprovado por eventos subsequentes). */
SELECT 
    t.nome_cientifico,
    r.codigo_anilha,
    COUNT(e.data_hora) AS qnt_eventos,
    NVL(SUM(n.n_ovos), 0) AS total_ovos
FROM Resgate_Encalhe r
JOIN Tartaruga t
    ON t.codigo_anilha = r.codigo_anilha
LEFT JOIN (
    SELECT codigo_anilha, data_hora
    FROM Pesca
    UNION ALL
    SELECT codigo_anilha, data_hora
    FROM Desova
) e
    ON e.codigo_anilha = r.codigo_anilha
   AND e.data_hora > r.data_hora
LEFT JOIN Desova d
    ON d.codigo_anilha = e.codigo_anilha
   AND d.data_hora = e.data_hora
LEFT JOIN Ninho n
    ON n.codigo_estaca = d.codigo_estaca
WHERE r.UF = 'BA'
  AND r.vivo = 'V'
  AND r.reabilitacao = 'V'
GROUP BY 
    t.nome_cientifico, 
    r.codigo_anilha
HAVING COUNT(e.data_hora) > 0;


/* CONSULTA 4: SUBCONSULTA DERIVADA COM AGREGAÇÃO
Objetivo: Retornar todos os pesquisadores, seus nomes, CPFs, no que 
atuam (resgate/encalhe, pesca ou desova), remunerações, formações e 
seus respectivos auxiliares.

Justificativa: Permite mapear as informações mais importantes 
relacionadas aos pesquisadores do projeto, evidenciando suas frentes 
de atuação e equipes de apoio em campo. */

SELECT 
    pes.Nome,
    pes.CPF,
    pesq.remuneracao,
    pesq.formacao,
    a.atuacoes,
    aux.cpfs_auxiliares,
    aux.nomes_auxiliares
FROM Pesquisador pesq
JOIN Pessoa pes
    ON pesq.CPF = pes.CPF
LEFT JOIN (
    SELECT 
        CPF_Pesq,
        LISTAGG(atuacao, ', ') WITHIN GROUP (ORDER BY atuacao) AS atuacoes
    FROM (
        SELECT DISTINCT CPF_Pesq, 'RESGATE' AS atuacao FROM Resgate_Encalhe
        UNION ALL
        SELECT DISTINCT CPF_Pesq, 'PESCA' FROM Pesca
        UNION ALL
        SELECT DISTINCT CPF_Pesq, 'DESOVA' FROM Desova
    )
    GROUP BY CPF_Pesq
) a
    ON a.CPF_Pesq = pesq.CPF
LEFT JOIN (
    SELECT 
        CPF_Pesq,
        LISTAGG(CPF_Func, ', ') WITHIN GROUP (ORDER BY CPF_Func) AS cpfs_auxiliares,
        LISTAGG(pes_aux.Nome, ', ') WITHIN GROUP (ORDER BY pes_aux.Nome) AS nomes_auxiliares
    FROM Auxilia aux
    JOIN Pessoa pes_aux
        ON aux.CPF_Func = pes_aux.CPF
    GROUP BY CPF_Pesq
) aux
    ON aux.CPF_Pesq = pesq.CPF
ORDER BY pes.Nome;


/* CONSULTA 5: RESUMO DAS BASES POR ESTADO (DASHBOARD)
Objetivo: Apresentar uma visão analítica de cada estado, incluindo 
unidades de atuação, arrecadação, pessoas atendidas, colaboradores, 
custos da equipe e indicadores de monitoramento ambiental.

Justificativa: Fornece uma visão gerencial de alto nível, permitindo 
cruzar o desempenho financeiro, estrutural e científico de cada Base 
Regional do projeto. */

WITH 
-- 1. ESTRUTURA FÍSICA
CTE_Lojas AS (SELECT UF, COUNT(*) AS qtd_lojas FROM Loja GROUP BY UF),
CTE_Museus AS (SELECT UF, COUNT(*) AS qtd_museus FROM Museu GROUP BY UF),
CTE_Areas AS (SELECT UF, COUNT(*) AS qtd_areas FROM Area_de_Monitoramento GROUP BY UF),

-- 2. FINANCEIRO E PÚBLICO
CTE_Pedidos AS (
    SELECT UF, SUM(valor) AS total_pedidos, COUNT(DISTINCT CPF) AS qtd_clientes 
    FROM Pedido GROUP BY UF
),
CTE_Ingressos AS (
    SELECT UF, SUM(valor) AS total_ingressos, COUNT(DISTINCT CPF) AS qtd_visitantes 
    FROM Ingresso GROUP BY UF
),

-- 3. RECURSOS HUMANOS E CUSTOS LOCAIS (Abordagem UNION + CASE WHEN)
CTE_Pesquisadores_UF AS (
    SELECT CPF_Pesq AS CPF, UF FROM Resgate_Encalhe UNION
    SELECT CPF_Pesq AS CPF, UF FROM Pesca UNION
    SELECT CPF_Pesq AS CPF, UF FROM Desova
),
CTE_Equipe_Itens AS (
    SELECT CPF, UF, 'FUNCIONARIO' AS tipo, NVL(remuneracao, 0) AS custo FROM Funcionario
    UNION ALL
    SELECT CPF, UF, 'ARTESAO' AS tipo, NVL(subsidio, 0) AS custo FROM Artesao
    UNION ALL
    SELECT pu.CPF, pu.UF, 'PESQUISADOR' AS tipo, NVL(p.remuneracao, 0) AS custo 
    FROM CTE_Pesquisadores_UF pu 
    JOIN Pesquisador p ON p.CPF = pu.CPF
),
CTE_Equipe AS (
    SELECT 
        UF,
        COUNT(DISTINCT CPF) AS total_colaboradores,
        COUNT(DISTINCT CASE WHEN tipo = 'FUNCIONARIO' THEN CPF END) AS qtd_funcionarios,
        COUNT(DISTINCT CASE WHEN tipo = 'PESQUISADOR' THEN CPF END) AS qtd_pesquisadores,
        COUNT(DISTINCT CASE WHEN tipo = 'ARTESAO' THEN CPF END) AS qtd_artesaos,
        SUM(custo) AS custo_equipe
    FROM CTE_Equipe_Itens
    GROUP BY UF
),

-- 4. MONITORAMENTO E CONSERVAÇÃO
CTE_Resgates AS (
    SELECT UF, COUNT(*) AS total_resgates, 
           SUM(CASE WHEN reabilitacao = 'V' THEN 1 ELSE 0 END) AS qtd_reab_resgate
    FROM Resgate_Encalhe GROUP BY UF
),
CTE_Pescas AS (
    SELECT UF, COUNT(*) AS total_pescas, 
           SUM(CASE WHEN classe = 'Monitorada' THEN 1 ELSE 0 END) AS pescas_monitoradas,
           SUM(CASE WHEN reabilitacao = 'V' THEN 1 ELSE 0 END) AS qtd_reab_pesca
    FROM Pesca GROUP BY UF
),
CTE_Desovas AS (
    SELECT d.UF, COUNT(d.codigo_anilha) AS total_desovas, 
           SUM(n.n_ovos) AS total_ovos, SUM(n.n_filhotes) AS total_filhotes
    FROM Desova d
    JOIN Ninho n ON d.codigo_estaca = n.codigo_estaca
    GROUP BY d.UF
),
CTE_Tartarugas AS (
    SELECT UF, COUNT(DISTINCT codigo_anilha) AS qtd_tartarugas
    FROM (
        SELECT UF, codigo_anilha FROM Resgate_Encalhe UNION
        SELECT UF, codigo_anilha FROM Pesca UNION
        SELECT UF, codigo_anilha FROM Desova
    ) GROUP BY UF
)

-- SELEÇÃO FINAL: CONSOLIDANDO TODAS AS CTEs POR ESTADO
SELECT 
    b.UF AS "Estado",

    -- Estrutura Física
    NVL(l.qtd_lojas, 0) AS "Lojas",
    NVL(m.qtd_museus, 0) AS "Museus",
    NVL(a.qtd_areas, 0) AS "Áreas de Monitoramento",

    -- Financeiro e Público
    NVL(p.total_pedidos, 0) + NVL(i.total_ingressos, 0) AS "Arrecadação Total (R$)",
    NVL(p.qtd_clientes, 0) AS "Clientes",
    NVL(i.qtd_visitantes, 0) AS "Visitantes",

    -- Equipe Base
    NVL(eq.qtd_funcionarios, 0) AS "Funcionários",
    NVL(eq.qtd_pesquisadores, 0) AS "Pesquisadores",
    NVL(eq.qtd_artesaos, 0) AS "Artesãos",
    NVL(eq.custo_equipe, 0) AS "Custo Equipe Local (R$)",

    -- Eventos Gerais
    NVL(r.total_resgates, 0) + NVL(pe.total_pescas, 0) + NVL(d.total_desovas, 0) AS "Total de Eventos",
    NVL(t.qtd_tartarugas, 0) AS "Tartarugas Monitoradas",

    -- Detalhamento de Resgates e Reabilitação
    NVL(r.total_resgates, 0) AS "Total Resgates",
    ROUND(NVL(r.total_resgates, 0) / NULLIF(a.qtd_areas, 0), 2) AS "Média Resgates/Área",
    ROUND(
        (NVL(r.qtd_reab_resgate, 0) + NVL(pe.qtd_reab_pesca, 0)) * 100.0 / 
        NULLIF(NVL(r.total_resgates, 0) + NVL(pe.total_pescas, 0), 0), 2
    ) AS "Taxa de Reabilitação (%)",

    -- Detalhamento de Pescas
    NVL(pe.total_pescas, 0) AS "Total Pescas",
    NVL(pe.pescas_monitoradas, 0) AS "Pescas Monitoradas",

    -- Detalhamento de Desovas
    NVL(d.total_desovas, 0) AS "Total Desovas",
    ROUND(NVL(d.total_filhotes, 0) * 100.0 / NULLIF(d.total_ovos, 0), 2) AS "Taxa de Eclosão (%)"

FROM (SELECT DISTINCT UF FROM Base) b
LEFT JOIN CTE_Lojas l ON b.UF = l.UF
LEFT JOIN CTE_Museus m ON b.UF = m.UF
LEFT JOIN CTE_Areas a ON b.UF = a.UF
LEFT JOIN CTE_Pedidos p ON b.UF = p.UF
LEFT JOIN CTE_Ingressos i ON b.UF = i.UF
LEFT JOIN CTE_Equipe eq ON b.UF = eq.UF 
LEFT JOIN CTE_Resgates r ON b.UF = r.UF
LEFT JOIN CTE_Pescas pe ON b.UF = pe.UF
LEFT JOIN CTE_Desovas d ON b.UF = d.UF
LEFT JOIN CTE_Tartarugas t ON b.UF = t.UF
ORDER BY b.UF;
