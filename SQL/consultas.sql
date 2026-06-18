-- Script: consultas.sql
-- Objetivo: Consultas de média/alta complexidade para o Projeto Tamar

/*CONSULTA 1: DIVISÃO RELACIONAL 
Objetivo: Listar o Nome e CPF dos Pesquisadores que já atuaram em 
resgates em TODAS as Áreas de Monitoramento do projeto.
 
Justificativa: Permite mapear os pesquisadores mais experientes e 
com maior mobilidade geográfica, fundamentais para liderar treinamentos 
nas diferentes bases litorâneas.*/

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
