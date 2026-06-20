-- Script: consultas.sql
-- Objetivo: Consultas de média/alta complexidade para o Projeto Tamar

/*CONSULTA 1: DIVISÃO RELACIONAL 
Objetivo: Listar o Nome e CPF dos Pesquisadores que já atuaram em 
resgates em TODAS as Áreas de Monitoramento do projeto.
 
Justificativa: Permite mapear os pesquisadores com maior mobilidade geográfica, 
fundamentais para liderar treinamentos nas diferentes regiões litorâneas.*/

SELECT p.Nome, p.CPF
FROM Pessoa p
JOIN Pesquisador pq ON p.CPF = pq.CPF
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

/*CONSULTA 2: ANINHADA CORRELACIONADA COM FOCO BIOLÓGICO/CONSERVAÇÃO)
Objetivo: Identificar as tartarugas e as áreas de monitoramento de 
seus ninhos que tiveram uma "taxa de eclosão" (percentual de filhotes)
SUPERIOR à taxa média de eclosão dos ninhos da MESMA ESPÉCIE

Justificativa: Indicador crucial de sucesso reprodutivo. Permite mapear 
matrizes (fêmeas) altamente férteis ou trechos de praia com condições 
de incubação ideais.*/
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
JOIN Ninho n1 ON d1.codigo_estaca = n1.codigo_estaca
JOIN Tartaruga t1 ON d1.codigo_anilha = t1.codigo_anilha
JOIN Especie e1 ON e1.nome_cientifico = t1.nome_cientifico
WHERE (n1.n_filhotes / n1.n_ovos) > (
    SELECT AVG(n2.n_filhotes / n2.n_ovos)
    FROM Desova d2
    JOIN Ninho n2 ON d2.codigo_estaca = n2.codigo_estaca
    JOIN Tartaruga t2 ON d2.codigo_anilha = t2.codigo_anilha
    WHERE t2.nome_cientifico = t1.nome_cientifico
);

/* CONSULTA 3: SUBCONSULTA DERIVADA COM AGREGAÇÃO
Objetivo: retornar todos os pesquisadores, seus nomes, CPFs, no que atuam (resgate, encalhe ou 
pesca), remunerações, formações e seus auxiliares 

Justificativa: Permite mapear as informações mais importantes relacionadas aos pesquisadores, como no que 
atuam e com quem.
*/
SELECT pes.Nome,
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
    SELECT CPF_Pesq,
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
    SELECT CPF_Pesq,
           LISTAGG(CPF_Func, ', ')  WITHIN GROUP (ORDER BY CPF_Func) AS cpfs_auxiliares,
           LISTAGG(pes_aux.Nome, ', ')  WITHIN GROUP (ORDER BY pes_aux.Nome) AS nomes_auxiliares
    FROM Auxilia aux
    JOIN Pessoa pes_aux
        ON aux.CPF_Func = pes_aux.CPF
    GROUP BY CPF_Pesq
) aux
    ON aux.CPF_Pesq = pesq.CPF
ORDER BY pes.Nome;

/* CONSULTA 4: RESUMO DAS BASES POR ESTADO 
Objetivo: Apresentar uma visão geral de cada base estadual, incluindo unidades de atuação, arrecadação, pessoas atendidas, 
colaboradores, custos da equipe e indicadores de monitoramento ambiental. 

Principais métricas visualizadas: 

- Quantidade de lojas, museus e áreas de monitoramento 
- Arrecadação de pedidos e ingressos 
- Quantidade de clientes e visitantes distintos 
- Funcionários, pesquisadores e artesãos associados ao estado 
- Total e média de resgates por área
- Taxa de reabilitação 
- Total de desovas e taxa de eclosão 
- Quantidade de pescas e tartarugas monitoradas 
- Total de eventos*/

-- design tabelas 
SET SQLBLANKLINES ON
SET LINESIZE 400
SET PAGESIZE 1000
SET WRAP OFF
SET TRIMSPOOL ON
SET TAB OFF
SET HEADING ON
SET FEEDBACK ON
SET COLSEP ' | '

COLUMN UF FORMAT A2
COLUMN CIDADE_BASE FORMAT A14
COLUMN LOJAS FORMAT 9990
COLUMN MUSEUS FORMAT 9990
COLUMN AREAS FORMAT 9990
COLUMN UNIDADES FORMAT 9990
COLUMN REC_LOJAS FORMAT 9999990D00
COLUMN REC_MUSEUS FORMAT 9999990D00
COLUMN ARREC_TOTAL FORMAT 9999990D00
COLUMN PESSOAS FORMAT 9999990
COLUMN TOTAL_FUNC FORMAT 9999990
COLUMN FUNC_MUSEU FORMAT 9999990
COLUMN PESQUISADORES FORMAT 9999990
COLUMN ARTESAOS FORMAT 9999990
COLUMN CUSTO_EQUIPE FORMAT 99999990D00
COLUMN RESGATES FORMAT 9999990
COLUMN MED_RES_AREA FORMAT 999990D00
COLUMN TX_REAB_RESG FORMAT 999990D00
COLUMN DESOVAS FORMAT 9999990
COLUMN TX_ECLOSAO FORMAT 999990D00
COLUMN PESCAS FORMAT 9999990
COLUMN TARTARUGAS FORMAT 9999990
COLUMN EVENTOS FORMAT 9999990

-- DISTINCT impede de contarmos o mesmo atributo mais de uma vez
WITH Estrutura_Base AS(
    SELECT b.UF, 
    COUNT(DISTINCT l.UF || '|' || l.cidade) AS lojas, 
    COUNT(DISTINCT m.UF || '|' || m.cidade) AS museus, 
    COUNT(DISTINCT a.UF || '|' || a.cidade) AS areas 
    FROM Base b
    LEFT JOIN Loja l 
    ON l.UF = b.UF
    LEFT JOIN Museu m 
    ON m.UF = b.UF
    LEFT JOIN Area_de_Monitoramento a 
    ON a.UF = b.UF
    GROUP BY b.UF
),

-- valor total arrecadado pelas lojas, quantidade total de pedidos realizados
-- NVL SE A COLUNA VALOR TIVER NULL SUBSTITUI POR 0, PRA NAO ATRAPALHAR NOSSA SOMA
Receita_Lojas AS(
    SELECT UF, SUM(NVL(valor,0)) AS receita,COUNT(*) AS pedidos FROM Pedido 
    GROUP BY UF
),

Receita_Museus AS (
    SELECT UF, SUM(NVL(valor, 0)) AS receita,COUNT(*) AS ingressos FROM Ingresso 
    GROUP BY UF),

Pessoas_Base AS(
    SELECT UF, COUNT(*) AS pessoas
    FROM (SELECT UF,CPF FROM Pedido UNION SELECT UF, CPF FROM Ingresso)
    GROUP BY UF),

Pesquisadores_Base AS (SELECT CPF_Pesq AS CPF, UF FROM Resgate_Encalhe 
    UNION 
    SELECT CPF_Pesq AS CPF, UF FROM Pesca 
    UNION 
    SELECT CPF_Pesq AS CPF, UF FROM Desova),

Equipe_Itens AS (
    SELECT CPF, UF, 'FUNCIONARIO' AS tipo,NVL(remuneracao, 0)AS custo FROM Funcionario
    UNION ALL
    SELECT CPF, UF, 'ARTESAO' AS tipo, NVL(subsidio, 0) AS custo FROM Artesao
    UNION ALL
    SELECT pb.CPF, pb.UF, 'PESQUISADOR' AS tipo, NVL(pq.remuneracao, 0) AS custo FROM Pesquisadores_Base pb JOIN Pesquisador pq ON pq.CPF = pb.CPF
),


Equipe_Base AS(SELECT UF,COUNT(DISTINCT CPF) AS colaboradores, 
    COUNT(DISTINCT CASE WHEN tipo = 'FUNCIONARIO' THEN CPF END) AS func_museu, 
    COUNT(DISTINCT CASE WHEN tipo = 'PESQUISADOR' THEN CPF END) AS pesquisadores, 
    COUNT(DISTINCT CASE WHEN tipo = 'ARTESAO' THEN CPF END) AS artesaos,SUM(custo) AS custo_equipe
    FROM Equipe_Itens
    GROUP BY UF),

Resgates_Area AS(
    SELECT a.UF, a.cidade,COUNT(r.codigo_anilha) AS total_resgates, SUM(CASE WHEN r.reabilitacao = 'V' THEN 1 ELSE 0 END) AS reabilitados
    FROM Area_de_Monitoramento a
    LEFT JOIN Resgate_Encalhe r ON r.UF = a.UF AND r.cidade = a.cidade
    GROUP BY a.UF, a.cidade
),
Resgates_Base AS(
    SELECT UF, SUM(total_resgates) AS resgates, ROUND(AVG(total_resgates), 2) AS med_res_area, ROUND(100 * SUM(reabilitados) / NULLIF(SUM(total_resgates), 0), 2) AS tx_reab_resg
    FROM Resgates_Area
    GROUP BY UF
),
Desovas_Base AS(
    SELECT d.UF, COUNT(*) AS desovas, ROUND(100*SUM(NVL(n.n_filhotes, 0))/NULLIF(SUM(NVL(n.n_ovos, 0)), 0), 2) AS tx_eclosao
    FROM Desova d
    JOIN Ninho n ON n.codigo_estaca = d.codigo_estaca
    GROUP BY d.UF
),

Pescas_Base AS(
    SELECT UF, COUNT(*) AS pescas FROM Pesca 
    GROUP BY UF
),
Tartarugas_Base AS(
    SELECT UF, COUNT(*) AS tartarugas
    FROM (
        SELECT UF, codigo_anilha FROM Resgate_Encalhe
        UNION
        SELECT UF, codigo_anilha FROM Pesca
        UNION
        SELECT UF, codigo_anilha FROM Desova
    )
    GROUP BY UF
)
SELECT b.UF, b.cidade AS cidade_base,
       NVL(es.lojas,0) AS lojas,NVL(es.museus, 0) AS museus, NVL(es.areas, 0) AS areas, NVL(es.lojas, 0) + NVL(es.museus, 0) + NVL(es.areas, 0) AS unidades,
       NVL(rl.receita, 0) AS rec_lojas, NVL(rm.receita, 0) AS rec_museus, NVL(rl.receita,0)+ NVL(rm.receita, 0) AS arrec_total,
       NVL(pb.pessoas,0) AS pessoas, NVL(eb.colaboradores,0) AS colaboradores, NVL(eb.func_museu,0) AS func_museu, NVL(eb.pesquisadores, 0) AS pesquisadores, NVL(eb.artesaos, 0) AS artesaos, NVL(eb.custo_equipe, 0) AS custo_equipe,
       NVL(rb.resgates, 0) AS resgates, NVL(rb.med_res_area, 0) AS med_res_area, NVL(rb.tx_reab_resg, 0) AS tx_reab_resg,
       NVL(db.desovas, 0) AS desovas, NVL(db.tx_eclosao,0) AS tx_eclosao, NVL(pes.pescas, 0) AS pescas, NVL(tb.tartarugas, 0) AS tartarugas,
       NVL(rb.resgates, 0) + NVL(db.desovas, 0) + NVL(pes.pescas,0) AS eventos
FROM Base b
LEFT JOIN Estrutura_Base es ON es.UF = b.UF
LEFT JOIN Receita_Lojas rl ON rl.UF = b.UF
LEFT JOIN Receita_Museus rm ON rm.UF = b.UF
LEFT JOIN Pessoas_Base pb ON pb.UF = b.UF
LEFT JOIN Equipe_Base eb ON eb.UF = b.UF
LEFT JOIN Resgates_Base rb ON rb.UF = b.UF
LEFT JOIN Desovas_Base db ON db.UF = b.UF
LEFT JOIN Pescas_Base pes ON pes.UF = b.UF
LEFT JOIN Tartarugas_Base tb ON tb.UF = b.UF
ORDER BY arrec_total DESC, b.UF;


/*Consulta 5: Tartarugas Reabilitadas com eventos Posteriores}
Objetivo: identificar tartarugas que, após passarem por um processo 
de reabilitação e serem registradas como vivas em um evento de resgate ou encalhe,
continuaram participando de atividades monitoradas de pesca ou desova após o processo de reabilitação */ 

SELECT t.nome_cientifico,
       r.codigo_anilha,
       COUNT(e.data_hora) AS qnt_eventos,
       NVL(SUM(n.n_ovos),0) AS total_ovos
FROM resgate_encalhe r
JOIN tartaruga t
    ON t.codigo_anilha = r.codigo_anilha
LEFT JOIN (
    SELECT codigo_anilha, data_hora
    FROM pesca
    UNION ALL
    SELECT codigo_anilha, data_hora
    FROM desova
) e
    ON e.codigo_anilha = r.codigo_anilha
   AND e.data_hora > r.data_hora
LEFT JOIN desova d
    ON d.codigo_anilha = e.codigo_anilha
   AND d.data_hora = e.data_hora
LEFT JOIN ninho n
    ON n.codigo_estaca = d.codigo_estaca
WHERE r.uf = 'BA'
  AND r.vivo = 'V'
  AND r.reabilitacao = 'V'
GROUP BY t.nome_cientifico, r.codigo_anilha
HAVING COUNT(e.data_hora) >=1 ;
