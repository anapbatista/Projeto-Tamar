-- Criação do Banco de Dados: Projeto Tamar

-- Tabela Base
CREATE TABLE Base (
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100),
    CONSTRAINT BS_PK PRIMARY KEY (UF)
);


--  Tabela Tipos (Suporte para Unidade de Atuação - NÃO TEM FK)
CREATE TABLE Tipos (
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    CONSTRAINT TP_PK PRIMARY KEY (UF, cidade, tipo)
);

-- Especializações de Unidade de Atuação

/*Não foi criada uma tabela generalista para Unidade de Atuação, 
o mapeamento foi feito diretamente nas tabelas especializadas (Loja, Museu e Área de Monitoramento), 
que herdam a identificação da entidade Base,conforme modelo relacional*/

CREATE TABLE Loja (
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CONSTRAINT LJ_PK PRIMARY KEY (UF, cidade),
    CONSTRAINT LJ_FK FOREIGN KEY (UF) REFERENCES Base(UF) ON DELETE CASCADE
);

CREATE TABLE Museu (
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CONSTRAINT MS_PK PRIMARY KEY (UF, cidade),
    CONSTRAINT MS_FK FOREIGN KEY (UF) REFERENCES Base(UF) ON DELETE CASCADE
);

CREATE TABLE Area_de_Monitoramento (
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    extensao_faixadeareia NUMBER,
    CONSTRAINT AM_PK PRIMARY KEY (UF, cidade),
    CONSTRAINT AM_FK FOREIGN KEY (UF) REFERENCES Base(UF) ON DELETE CASCADE
);


--  Tabelas Espécie e Tartaruga
CREATE TABLE Especie (
    nome_cientifico VARCHAR(100) NOT NULL,
    nivel_de_extincao VARCHAR(50),
    CONSTRAINT EP_PK PRIMARY KEY (nome_cientifico)
);

CREATE TABLE Tartaruga (
    codigo_anilha VARCHAR(50) NOT NULL,
    peso NUMBER,
    tamanho_casco NUMBER,
    sexo CHAR(1),
    nome_cientifico VARCHAR(100) NOT NULL,
    CONSTRAINT TT_PK PRIMARY KEY (codigo_anilha),
    CONSTRAINT TT_FK FOREIGN KEY (nome_cientifico) REFERENCES Especie(nome_cientifico)
);


-- Tabela Pessoa (Generalista)
CREATE TABLE Pessoa (
    CPF VARCHAR(11) NOT NULL,
    Nome VARCHAR(100) NOT NULL,
    Data_nascim DATE,
    Funcao VARCHAR(50),
    Prioridade_lei VARCHAR(50), -- Pode ser nulo caso não se enquadre
    CONSTRAINT PS_PK PRIMARY KEY (CPF)
);


-- Especializações de Pessoa
CREATE TABLE Artesao (
    CPF VARCHAR(11) NOT NULL,
    subsidio NUMBER,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CONSTRAINT AT_PK PRIMARY KEY (CPF),
    CONSTRAINT AT_FK1 FOREIGN KEY (CPF) REFERENCES Pessoa(CPF) ON DELETE CASCADE,
    CONSTRAINT AT_FK2 FOREIGN KEY (UF, cidade) REFERENCES Loja(UF, cidade)
);

CREATE TABLE Produtos (
    CPF VARCHAR(11) NOT NULL,
    produto VARCHAR(50) NOT NULL,
    CONSTRAINT PR_PK PRIMARY KEY (CPF, produto),
    CONSTRAINT PR_FK FOREIGN KEY (CPF) REFERENCES Artesao(CPF) ON DELETE CASCADE
);

/*O atributo data_fim da entidade Funcionário não foi armazenado no banco de dados, 
pois pode ser calculado a partir da data de início e do tipo de atuação.*/

CREATE TABLE Funcionario (
    CPF VARCHAR(11) NOT NULL,
    data_ini DATE,
    atuacao VARCHAR(50),
    remuneracao NUMBER,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CONSTRAINT FC_PK PRIMARY KEY (CPF),
    CONSTRAINT FC_FK1 FOREIGN KEY (CPF) REFERENCES Pessoa(CPF) ON DELETE CASCADE,
    CONSTRAINT FC_FK2 FOREIGN KEY (UF, cidade) REFERENCES Museu(UF, cidade)
);

CREATE TABLE Pesquisador (
    CPF VARCHAR(11) NOT NULL,
    formacao VARCHAR(100),
    remuneracao NUMBER,
    CONSTRAINT PQ_PK PRIMARY KEY (CPF),
    CONSTRAINT PQ_FK FOREIGN KEY (CPF) REFERENCES Pessoa(CPF) ON DELETE CASCADE
);

CREATE TABLE Auxilia (
    CPF_Func VARCHAR(11) NOT NULL,
    CPF_Pesq VARCHAR(11) NOT NULL,
    CONSTRAINT AX_PK PRIMARY KEY (CPF_Func, CPF_Pesq),
    CONSTRAINT AX_FK1 FOREIGN KEY (CPF_Func) REFERENCES Funcionario(CPF),
    CONSTRAINT AX_FK2 FOREIGN KEY (CPF_Pesq) REFERENCES Pesquisador(CPF)
);

-- Interações Comerciais e de Visitação (Ciclos)
CREATE TABLE Vende_para (
    CPF VARCHAR(11) NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CONSTRAINT VD_PK PRIMARY KEY (CPF, UF, cidade),
    CONSTRAINT VD_FK1 FOREIGN KEY (CPF) REFERENCES Pessoa(CPF),
    CONSTRAINT VD_FK2 FOREIGN KEY (UF, cidade) REFERENCES Loja(UF, cidade)
);

CREATE TABLE Pedido (
    CPF VARCHAR(11) NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    valor NUMBER,
    CONSTRAINT PD_PK PRIMARY KEY (CPF, UF, cidade, data_hora),
    CONSTRAINT PD_FK FOREIGN KEY (CPF, UF, cidade) REFERENCES Vende_para(CPF, UF, cidade) ON DELETE CASCADE
);

CREATE TABLE Visita (
    CPF VARCHAR(11) NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CONSTRAINT VS_PK PRIMARY KEY (CPF, UF, cidade),
    CONSTRAINT VS_FK1 FOREIGN KEY (CPF) REFERENCES Pessoa(CPF),
    CONSTRAINT VS_FK2 FOREIGN KEY (UF, cidade) REFERENCES Museu(UF, cidade)
);

CREATE TABLE Ingresso (
    CPF VARCHAR(11) NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    valor NUMBER,
    categoria VARCHAR(50),
    CONSTRAINT IG_PK PRIMARY KEY (CPF, UF, cidade, data_hora),
    CONSTRAINT IG_FK FOREIGN KEY (CPF, UF, cidade) REFERENCES Visita(CPF, UF, cidade) ON DELETE CASCADE
);


--  Eventos e Classificações 

/*O mapeamento foi realizado nas tabelas das entidades especializadas (Resgate/Encalhe, Pesca e Desova), 
que contêm os atributos específicos e os comuns, além de uma tabela de suporte Classificacoes
para garantir a restrição de disjunção, conforme modelo relacional*/

CREATE TABLE Classificacoes ( -- TABELA SUPORTE, NÃO TEM FK
    codigo_anilha VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP NOT NULL, -- Registrado com precisão de hora inteira
    classificacao VARCHAR(50) NOT NULL,
    CONSTRAINT CS_PK PRIMARY KEY (codigo_anilha, data_hora)
);

CREATE TABLE Ninho (
    codigo_estaca VARCHAR(50) NOT NULL,
    lat_long VARCHAR(100),
    n_ovos INT,
    n_filhotes INT,
    CONSTRAINT NH_PK PRIMARY KEY (codigo_estaca)
);

-- Especializações de Evento

/*Os atributos referentes a "reabilitação" e "vivo" foram modelados como booleanos, 
onde o valor verdadeiro indica, respectivamente, 
o encaminhamento para reabilitação e que o animal foi encontrado vivo.*/

CREATE TABLE Resgate_Encalhe (
    codigo_anilha VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CPF_Pesq VARCHAR(11) NOT NULL,
    motivo VARCHAR(200),
    vivo CHAR(1),
    reabilitacao CHAR(1),
    CONSTRAINT RE_PK PRIMARY KEY (codigo_anilha, data_hora),
    CONSTRAINT RE_FK1 FOREIGN KEY (UF, cidade) REFERENCES Area_de_Monitoramento(UF, cidade),
    CONSTRAINT RE_FK2 FOREIGN KEY (CPF_Pesq) REFERENCES Pesquisador(CPF)
);

CREATE TABLE Pesca (
    codigo_anilha VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CPF_Pesq VARCHAR(11) NOT NULL,
    classe VARCHAR(50),
    reabilitacao CHAR(1),
    CONSTRAINT PC_PK PRIMARY KEY (codigo_anilha, data_hora),
    CONSTRAINT PC_FK1 FOREIGN KEY (UF, cidade) REFERENCES Area_de_Monitoramento(UF, cidade),
    CONSTRAINT PC_FK2 FOREIGN KEY (CPF_Pesq) REFERENCES Pesquisador(CPF)
);

CREATE TABLE Desova (
    codigo_anilha VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    UF CHAR(2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    CPF_Pesq VARCHAR(11) NOT NULL,
    codigo_estaca VARCHAR(50) NOT NULL UNIQUE, -- Restrição de unicidade para a relação 1:1 com Ninho
    CONSTRAINT DS_PK PRIMARY KEY (codigo_anilha, data_hora),
    CONSTRAINT DS_FK1 FOREIGN KEY (UF, cidade) REFERENCES Area_de_Monitoramento(UF, cidade),
    CONSTRAINT DS_FK2 FOREIGN KEY (CPF_Pesq) REFERENCES Pesquisador(CPF),
    CONSTRAINT DS_FK3 FOREIGN KEY (codigo_estaca) REFERENCES Ninho(codigo_estaca)
);
