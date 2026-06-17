-- Script: dados.sql
-- Objetivo: Alimentação inicial da base de dados do Projeto Tamar

-- Alimentação da Tabela Base
INSERT INTO Base (UF, cidade) VALUES ('BA', 'Salvador');
INSERT INTO Base (UF, cidade) VALUES ('ES', 'Vitória');

--  Alimentação da Tabela Tipos
INSERT INTO Tipos (UF, cidade, tipo) VALUES ('BA', 'Praia do Forte', 'Loja');
INSERT INTO Tipos (UF, cidade, tipo) VALUES ('BA', 'Arembepe', 'Museu');
INSERT INTO Tipos (UF, cidade, tipo) VALUES ('BA', 'Arembepe', 'Área de Monitoramento');
INSERT INTO Tipos (UF, cidade, tipo) VALUES ('ES', 'Guriri', 'Museu');
INSERT INTO Tipos (UF, cidade, tipo) VALUES ('ES', 'Regência', 'Loja');
INSERT INTO Tipos (UF, cidade, tipo) VALUES ('ES', 'Vitória', 'Área de Monitoramento');

--  Alimentação das Especializações de Unidade de Atuação
INSERT INTO Loja (UF, cidade) VALUES ('BA', 'Praia do Forte');
INSERT INTO Loja (UF, cidade) VALUES ('ES', 'Regência');

INSERT INTO Museu (UF, cidade) VALUES ('BA', 'Arembepe');
INSERT INTO Museu (UF, cidade) VALUES ('ES', 'Guriri');

INSERT INTO Area_de_Monitoramento (UF, cidade, extensao_faixadeareia) VALUES ('BA', 'Arembepe', 45.5);
INSERT INTO Area_de_Monitoramento (UF, cidade, extensao_faixadeareia) VALUES ('ES', 'Vitória', 30.0);

-- Alimentação das Tabelas Espécie e Tartaruga
INSERT INTO Especie (nome_cientifico, nivel_de_extincao) VALUES ('Caretta caretta', 'Vulnerável');
INSERT INTO Especie (nome_cientifico, nivel_de_extincao) VALUES ('Chelonia mydas', 'Em Perigo');

INSERT INTO Tartaruga (codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico) VALUES ('BR0001', 85.0, 90.5, 'F', 'Caretta caretta');
INSERT INTO Tartaruga (codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico) VALUES ('BR0002', 110.0, 105.0, 'M', 'Chelonia mydas');
-- Inserindo uma terceira tartaruga fêmea para os dois eventos de desova
INSERT INTO Tartaruga (codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico) VALUES ('BR0003', 75.5, 88.0, 'F', 'Caretta caretta');
INSERT INTO Tartaruga (codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico) VALUES ('BR0004', 60.0, 75.0, 'F', 'Caretta caretta');
INSERT INTO Tartaruga (codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico) VALUES ('BR0005', 45.0, 60.0, 'M', 'Chelonia mydas');

-- Alimentação da Tabela Pessoa (Generalista)
-- Pessoas que serão Artesãos
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('11111111111', 'Ana Maria', TO_DATE('1980-05-10', 'YYYY-MM-DD'), 'Artesão', NULL);
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('22222222222', 'José Silva', TO_DATE('1975-08-22', 'YYYY-MM-DD'), 'Artesão', NULL);

-- Pessoas que serão Funcionários
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('33333333333', 'Carlos Souza', TO_DATE('1990-11-15', 'YYYY-MM-DD'), 'Funcionário', NULL);
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('44444444444', 'Beatriz Lima', TO_DATE('1995-02-28', 'YYYY-MM-DD'), 'Funcionário', 'Gestante');
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('99999999999', 'João Alves', TO_DATE('2001-03-12', 'YYYY-MM-DD'), 'Funcionário', NULL);
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('10101010101', 'Carla Mendes', TO_DATE('2002-09-01', 'YYYY-MM-DD'), 'Funcionário', NULL);

-- Pessoas que serão Pesquisadores
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('55555555555', 'Fernanda Carrilho', TO_DATE('1985-07-30', 'YYYY-MM-DD'), 'Pesquisador', NULL);
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('66666666666', 'Roberto Vargas', TO_DATE('1982-12-10', 'YYYY-MM-DD'), 'Pesquisador', NULL);
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('12121212121', 'Marcos Sênior', TO_DATE('1970-03-22', 'YYYY-MM-DD'), 'Pesquisador', NULL);

-- Pessoas que serão Visitantes/Clientes
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('77777777777', 'Marcos Paulo', TO_DATE('2000-01-20', 'YYYY-MM-DD'), NULL, 'Estudante');
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('88888888888', 'Lucia Alves', TO_DATE('1960-04-12', 'YYYY-MM-DD'), NULL, 'Idoso');
INSERT INTO Pessoa (CPF, Nome, Data_nascim, Funcao, Prioridade_lei) VALUES ('12312312312', 'Helena Costa', TO_DATE('1992-08-14', 'YYYY-MM-DD'), NULL, NULL);

-- Alimentação das Especializações de Pessoa
INSERT INTO Artesao (CPF, subsidio, UF, cidade) VALUES ('11111111111', 500.00, 'BA', 'Praia do Forte');
INSERT INTO Artesao (CPF, subsidio, UF, cidade) VALUES ('22222222222', 650.00, 'ES', 'Regência');

INSERT INTO Produtos (CPF, produto) VALUES ('11111111111', 'Escultura de Tartaruga');
INSERT INTO Produtos (CPF, produto) VALUES ('22222222222', 'Camiseta Tamar');

INSERT INTO Funcionario (CPF, data_ini, atuacao, remuneracao, UF, cidade) VALUES ('33333333333', TO_DATE('2026-01-10', 'YYYY-MM-DD'), 'Estágio', 900.00, 'BA', 'Arembepe');
INSERT INTO Funcionario (CPF, data_ini, atuacao, remuneracao, UF, cidade) VALUES ('44444444444', TO_DATE('2026-05-15', 'YYYY-MM-DD'), 'Estágio', 1100.00, 'ES', 'Guriri');
INSERT INTO Funcionario (CPF, data_ini, atuacao, remuneracao, UF, cidade) VALUES ('99999999999', TO_DATE('2026-06-14', 'YYYY-MM-DD'), 'Estágio', 900.00, 'BA', 'Arembepe');
INSERT INTO Funcionario (CPF, data_ini, atuacao, remuneracao, UF, cidade) VALUES ('10101010101', TO_DATE('2025-11-05', 'YYYY-MM-DD'), 'Estágio', 1100.00, 'ES', 'Guriri');

INSERT INTO Pesquisador (CPF, formacao, remuneracao) VALUES ('55555555555', 'Biologia Marinha', 7500.00);
INSERT INTO Pesquisador (CPF, formacao, remuneracao) VALUES ('66666666666', 'Oceanografia', 8000.00);
INSERT INTO Pesquisador (CPF, formacao, remuneracao) VALUES ('12121212121', 'Doutorado em Biologia Marinha', 12000.00);

INSERT INTO Auxilia (CPF_Func, CPF_Pesq) VALUES ('99999999999', '55555555555');
INSERT INTO Auxilia (CPF_Func, CPF_Pesq) VALUES ('10101010101', '66666666666');

-- Alimentação de Interações Comerciais e Visitação
INSERT INTO Vende_para (CPF, UF, cidade) VALUES ('77777777777', 'BA', 'Praia do Forte');
INSERT INTO Vende_para (CPF, UF, cidade) VALUES ('88888888888', 'ES', 'Regência');
INSERT INTO Vende_para (CPF, UF, cidade) VALUES ('12312312312', 'BA', 'Praia do Forte');
INSERT INTO Vende_para (CPF, UF, cidade) VALUES ('12312312312', 'ES', 'Regência');

INSERT INTO Pedido (CPF, UF, cidade, data_hora, valor) VALUES ('77777777777', 'BA', 'Praia do Forte', TO_TIMESTAMP('2024-06-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS'), 120.50);
INSERT INTO Pedido (CPF, UF, cidade, data_hora, valor) VALUES ('88888888888', 'ES', 'Regência', TO_TIMESTAMP('2024-06-16 10:15:00', 'YYYY-MM-DD HH24:MI:SS'), 85.00);
INSERT INTO Pedido (CPF, UF, cidade, data_hora, valor) VALUES ('12312312312', 'BA', 'Praia do Forte', TO_TIMESTAMP('2024-07-01 10:00:00', 'YYYY-MM-DD HH24:MI:SS'), 150.00);
INSERT INTO Pedido (CPF, UF, cidade, data_hora, valor) VALUES ('12312312312', 'ES', 'Regência', TO_TIMESTAMP('2024-07-05 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), 200.00);

INSERT INTO Visita (CPF, UF, cidade) VALUES ('77777777777', 'BA', 'Arembepe');
INSERT INTO Visita (CPF, UF, cidade) VALUES ('88888888888', 'ES', 'Guriri');

INSERT INTO Ingresso (CPF, UF, cidade, data_hora, valor, categoria) VALUES ('77777777777', 'BA', 'Arembepe', TO_TIMESTAMP('2024-06-15 13:00:00', 'YYYY-MM-DD HH24:MI:SS'), 20.00, 'Meia');
INSERT INTO Ingresso (CPF, UF, cidade, data_hora, valor, categoria) VALUES ('88888888888', 'ES', 'Guriri', TO_TIMESTAMP('2024-06-16 09:30:00', 'YYYY-MM-DD HH24:MI:SS'), 0.00, 'Gratuidade');

-- Alimentação de Eventos e Classificações (Tabelas Relacionadas a Monitoramento)
-- Registrando os eventos na tabela de suporte Classificacoes
INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0001', TO_TIMESTAMP('2024-05-01 08:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Resgate');
INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0002', TO_TIMESTAMP('2024-05-02 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Resgate');

INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0001', TO_TIMESTAMP('2024-05-10 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Pesca');
INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0002', TO_TIMESTAMP('2024-05-11 16:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Pesca');

INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0001', TO_TIMESTAMP('2024-06-01 23:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Desova');
INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0003', TO_TIMESTAMP('2024-06-05 22:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Desova');

INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0004', TO_TIMESTAMP('2024-08-10 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Resgate');
INSERT INTO Classificacoes (codigo_anilha, data_hora, classificacao) VALUES ('BR0005', TO_TIMESTAMP('2024-08-15 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'Resgate');

-- Alimentando a tabela Ninho (Necessária para associar à Desova)
INSERT INTO Ninho (codigo_estaca, lat_long, n_ovos, n_filhotes) VALUES ('EST-001', '-12.57, -38.00', 115, 80);
INSERT INTO Ninho (codigo_estaca, lat_long, n_ovos, n_filhotes) VALUES ('EST-002', '-10.95, -37.04', 125, 105);

-- Inserindo nas Entidades Especializadas de Evento
INSERT INTO Resgate_Encalhe (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, motivo, vivo, reabilitacao) VALUES ('BR0001', TO_TIMESTAMP('2024-05-01 08:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'BA', 'Arembepe', '55555555555', 'Presa em rede de emalhe', 'V', 'V');
INSERT INTO Resgate_Encalhe (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, motivo, vivo, reabilitacao) VALUES ('BR0002', TO_TIMESTAMP('2024-05-02 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'ES', 'Vitória', '66666666666', 'Ingestão de plástico', 'V', 'V');
INSERT INTO Resgate_Encalhe (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, motivo, vivo, reabilitacao) VALUES ('BR0004', TO_TIMESTAMP('2024-08-10 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'BA', 'Arembepe', '12121212121', 'Presa em rede fantasma', 'V', 'V');
INSERT INTO Resgate_Encalhe (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, motivo, vivo, reabilitacao) VALUES ('BR0005', TO_TIMESTAMP('2024-08-15 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'ES', 'Vitória', '12121212121', 'Debilidade natural', 'V', 'V');

INSERT INTO Pesca (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, classe, reabilitacao) VALUES ('BR0001', TO_TIMESTAMP('2024-05-10 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'BA', 'Arembepe', '55555555555', 'Não Monitorada', 'F');
INSERT INTO Pesca (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, classe, reabilitacao) VALUES ('BR0002', TO_TIMESTAMP('2024-05-11 16:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'ES', 'Vitória', '66666666666', 'Monitorada', 'F');

INSERT INTO Desova (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, codigo_estaca) VALUES ('BR0001', TO_TIMESTAMP('2024-06-01 23:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'BA', 'Arembepe', '55555555555', 'EST-001');
INSERT INTO Desova (codigo_anilha, data_hora, UF, cidade, CPF_Pesq, codigo_estaca) VALUES ('BR0003', TO_TIMESTAMP('2024-06-05 22:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'ES', 'Vitória', '55555555555', 'EST-002');

COMMIT;
