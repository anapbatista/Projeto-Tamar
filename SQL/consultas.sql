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
