-- Script: consultas.sql
-- Objetivo: Consultas de média/alta complexidade para o Projeto Tamar

/*CONSULTA 1: DIVISÃO RELACIONAL
Objetivo: Listar o Nome e o CPF dos clientes (Pessoas) que realizaram
pedidos em TODAS as lojas cadastradas no sistema.

Justificativa: Ideal para identificar "super apoiadores" do Projeto Tamar,
ou seja, consumidores extremamente fiéis que viajam e consomem produtos 
de artesãos em absolutamente todas as filiais comerciais.*/

SELECT p.Nome, p.CPF
FROM PESSOA p
WHERE NOT EXISTS (
    SELECT l.UF, l.cidade
    FROM LOJA l
    WHERE NOT EXISTS (
        SELECT 1
        FROM PEDIDO pd
        WHERE pd.CPF = p.CPF
          AND pd.UF = l.UF
          AND pd.cidade = l.cidade
    )
);

/*CONSULTA 2: DIVISÃO RELACIONAL 
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
