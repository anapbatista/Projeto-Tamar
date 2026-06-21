# Projeto Tamar 

Bem-vindo ao repositório do **Projeto Tamar**. Este projeto consiste na modelagem e implementação de um Banco de Dados Relacional (Oracle) integrado a uma aplicação de linha de comando (CLI) desenvolvida em Python. O objetivo principal é gerenciar e unificar os dados das frentes comerciais (lojas e museus) e biológicas (monitoramento, resgate e conservação de tartarugas marinhas) do projeto.

---

## Índice

* [Sobre o Projeto](https://www.google.com/search?q=%23-sobre-o-projeto)
* [Estrutura do Repositório](https://www.google.com/search?q=%23-estrutura-do-reposit%C3%B3rio)
* [Principais Funcionalidades](https://www.google.com/search?q=%23-principais-funcionalidades)
* [Pré-requisitos](https://www.google.com/search?q=%23-pr%C3%A9-requisitos)
* [Como Executar a Aplicação](https://www.google.com/search?q=%23-como-executar-a-aplica%C3%A7%C3%A3o)
* [Tecnologias Utilizadas](https://www.google.com/search?q=%23-tecnologias-utilizadas)

---

## Sobre o Projeto

O sistema foi desenhado para resolver o desafio de fragmentação de dados das bases regionais do Projeto Tamar. Através de um esquema relacional robusto, é possível rastrear desde o faturamento de uma loja de *souvenirs* e a atuação de funcionários e artesãos, até a biometria de tartarugas resgatadas, taxas de eclosão de ninhos e protocolos de reabilitação.

---

## Estrutura do Repositório

O repositório está organizado em diretórios semânticos para facilitar a navegação e execução:

* **`SQL/`**: Contém todos os scripts de implementação no Oracle Database.
* `esquema.sql`: Criação das tabelas, chaves primárias (PK), chaves estrangeiras (FK) e restrições (Constraints).
* `dados.sql`: Script de população do banco de dados com uma carga inicial de testes.
* `consultas.sql`: Consultas de média e alta complexidade, incluindo divisões relacionais, agregações e CTEs que funcionam como *dashboards* analíticos.


* **`Application/`**: Contém o código-fonte da aplicação interativa.
* `app.py`: Arquivo principal (ponto de entrada) contendo a interface de terminal e a lógica de negócio estruturada em funções.
* `requirements.txt`: Mapeamento das bibliotecas e dependências Python do projeto.


* **`/` (Raiz)**: Documentação em texto/PDF referente ao levantamento de requisitos, diagramas de Entidade-Relacionamento (DER) e o relatório final.

---

##  Principais Funcionalidades

###  Módulo Comercial (Lojas e Museus)

* Registro de vendas de produtos e emissão de ingressos.
* Cadastro autônomo de clientes e visitantes, com gestão de prioridade por lei (idosos, estudantes, etc.).

###  Módulo de Conservação (Áreas de Monitoramento)

* **Resgates e Encalhes:** Registro de ocorrências, motivo e status vital da tartaruga.
* **Pescas:** Monitoramento de capturas acidentais e triagem para reabilitação preventiva.
* **Desovas:** Cadastro de matrizes, ninhos (estacas), coordenadas e cálculo de taxa de eclosão (ovos vs. filhotes vivos).
* **Histórico Unificado:** Consulta global da vida de uma tartaruga por meio do código da anilha.
* **Estatísticas Locais:** Geração de relatórios consolidados em tempo real sobre a eficiência reprodutiva e de resgates da unidade.

---

## Pré-requisitos

Para rodar este projeto na sua máquina, você precisará de:

* **Python 3.7+** instalado.
* Conexão ativa com a internet (para baixar pacotes pip).
* Credenciais de acesso a um banco de dados **Oracle** (Usuário, Senha, Host, Porta e Service Name).

---

## Como Executar a Aplicação

Siga o passo a passo abaixo para rodar a aplicação localmente:

**1. Clone o repositório:**

```bash
git clone https://github.com/anapbatista/Projeto-Tamar.git
cd Projeto-Tamar/Application

```

**2. Crie e ative um ambiente virtual (Opcional, mas recomendado):**

* No Windows:
```bash
python -m venv venv
venv\Scripts\activate

```


* No Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate

```



**3. Instale as dependências requeridas:**
Isso fará o download da biblioteca `oracledb` (modo *Thin*, que não exige instalação de clientes Oracle pesados na sua máquina).

```bash
pip install -r requirements.txt

```

**4. Inicie o sistema:**
É necessário saber a senha de acesso ao Banco de Dados Oracle

```bash
python app.py

```

---

## Tecnologias Utilizadas

* **Linguagem Principal:** Python 3
* **Banco de Dados:** Oracle SQL
* **Comunicação DB/Aplicação:** Biblioteca nativa `oracledb`
* **Paradigma da Aplicação:** Command Line Interface (CLI) Modular

---

*Este projeto é acadêmico e desenvolvido para a Disciplina de Base de Dados (1º semestre de 2026)*
