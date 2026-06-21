from database import conectar
from datetime import datetime

# UTILIDADES

def selecionar_unidade(conn, tabela, nome_unidade):

    try:
        with conn.cursor() as cursor:

            cursor.execute(f"""
                SELECT UF, CIDADE
                FROM {tabela}
                ORDER BY UF, CIDADE
            """)

            unidades = cursor.fetchall()

            if not unidades:
                print(f"\nNenhuma unidade de {nome_unidade} cadastrada.")
                return None

            print(f"\n=== {nome_unidade.upper()} ===")

            for i, (uf, cidade) in enumerate(unidades, start=1):
                print(f"{i} - {uf} - {cidade}")

            print("0 - Voltar")

            try:
                opcao = int(input("\nEscolha uma unidade: "))
            except ValueError:
                print("Digite um número válido.")
                return None

            if opcao == 0:
                return None

            if opcao < 1 or opcao > len(unidades):
                print("Opção inválida.")
                return None

            uf, cidade = unidades[opcao - 1]

            return {
                "uf": uf,
                "cidade": cidade
            }

    except Exception as e:
        print(f"Erro: {e}")
        return None

# funções lojas
def registrar_pedido(conn, unidade):

    try:

        cpf = input("\nCPF do cliente: ").strip()

        if not cpf.isdigit():
            print("CPF deve conter apenas números.")
            return

        with conn.cursor() as cursor:

            # Verifica se a pessoa existe

            cursor.execute("""
                SELECT NOME
                FROM PESSOA
                WHERE CPF = :cpf
            """, {"cpf": cpf})

            resultado = cursor.fetchone()

            if resultado is None:

                print("\nCliente não encontrado.")
                print("=== NOVO CADASTRO ===")

                nome = input("Nome: ").strip()

                data_nasc = input(
                    "Data de nascimento (DD/MM/YYYY): "
                ).strip()

                while True:

                    print("\nPrioridade por lei")
                    print("1 - Nenhuma")
                    print("2 - Estudante")
                    print("3 - Idoso")
                    print("4 - Gestante")

                    opc = input("Opção: ").strip()

                    if opc in ["1", "2", "3", "4"]:
                        break

                    print("Opção inválida.")

                prioridade = None

                if opc == "2":
                    prioridade = "Estudante"
                elif opc == "3":
                    prioridade = "Idoso"
                elif opc == "4":
                    prioridade = "Gestante"

                cursor.execute("""
                    INSERT INTO PESSOA (
                        CPF,
                        NOME,
                        DATA_NASCIM,
                        FUNCAO,
                        PRIORIDADE_LEI
                    )
                    VALUES (
                        :cpf,
                        :nome,
                        TO_DATE(:data_nasc,'DD/MM/YYYY'),
                        NULL,
                        :prioridade
                    )
                """, {
                    "cpf": cpf,
                    "nome": nome,
                    "data_nasc": data_nasc,
                    "prioridade": prioridade
                })

                print("\nCliente cadastrado com sucesso.")

            else:

                nome = resultado[0]

                cursor.execute("""
                    SELECT PRIORIDADE_LEI
                    FROM PESSOA
                    WHERE CPF = :cpf
                """, {"cpf": cpf})

                prioridade = cursor.fetchone()[0]

            # Verifica se já existe relacionamento VENDE

            cursor.execute("""
                SELECT 1
                FROM VENDE_PARA
                WHERE CPF = :cpf
                  AND UF = :uf
                  AND CIDADE = :cidade
            """, {
                "cpf": cpf,
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            if cursor.fetchone() is None:

                cursor.execute("""
                    INSERT INTO VENDE_PARA (
                        CPF,
                        UF,
                        CIDADE
                    )
                    VALUES (
                        :cpf,
                        :uf,
                        :cidade
                    )
                """, {
                    "cpf": cpf,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"]
                })

            while True:

                try:

                    valor = float(
                        input(
                            "Valor do pedido: R$ "
                        ).replace(",", ".")
                    )

                    if valor <= 0:
                        print(
                            "O valor deve ser maior que zero."
                        )
                        continue

                    break

                except ValueError:

                    print("Valor inválido.")

            cursor.execute("""
                INSERT INTO PEDIDO (
                    CPF,
                    UF,
                    CIDADE,
                    DATA_HORA,
                    VALOR
                )
                VALUES (
                    :cpf,
                    :uf,
                    :cidade,
                    SYSDATE,
                    :valor
                )
            """, {
                "cpf": cpf,
                "uf": unidade["uf"],
                "cidade": unidade["cidade"],
                "valor": valor
            })

        conn.commit()

        momento = datetime.now()

        print("\n====================================")
        print("          PROJETO TAMAR")
        print("====================================")
        print("Pedido registrado com sucesso")
        print("------------------------------------")
        print(f"Cliente......: {nome}")
        print(f"CPF..........: {cpf}")

        if prioridade:
            print(f"Prioridade...: {prioridade}")
        else:
            print("Prioridade...: Nenhuma")

        print(
            f"Loja.........: "
            f"{unidade['uf']} - {unidade['cidade']}"
        )

        print(f"Valor........: R$ {valor:.2f}")

        print(
            "Data/Hora....: "
            f"{momento.strftime('%d/%m/%Y %H:%M:%S')}"
        )

        print("====================================")

    except Exception as e:

        conn.rollback()

        print("\nErro ao registrar pedido.")
        print(e)

def consultar_faturamento_loja(conn, unidade):

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    COUNT(*) AS quantidade_pedidos,
                    NVL(SUM(VALOR), 0) AS faturamento_total,
                    NVL(AVG(VALOR), 0) AS ticket_medio,
                    NVL(MIN(VALOR), 0) AS menor_pedido,
                    NVL(MAX(VALOR), 0) AS maior_pedido
                FROM PEDIDO
                WHERE UF = :uf
                  AND CIDADE = :cidade
                  AND EXTRACT(MONTH FROM DATA_HORA) =
                      EXTRACT(MONTH FROM SYSDATE)
                  AND EXTRACT(YEAR FROM DATA_HORA) =
                      EXTRACT(YEAR FROM SYSDATE)
            """, {
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            resultado = cursor.fetchone()

            qtd_pedidos = resultado[0]
            faturamento = resultado[1]
            ticket_medio = resultado[2]
            menor_pedido = resultado[3]
            maior_pedido = resultado[4]

            print("\n====================================")
            print(" FATURAMENTO MENSAL")
            print("====================================")
            print(f"Loja: {unidade['cidade']} - {unidade['uf']}")
            print("------------------------------------")
            print(f"Pedidos no mês : {qtd_pedidos}")
            print(f"Faturamento    : R$ {faturamento:.2f}")
            print(f"Ticket médio   : R$ {ticket_medio:.2f}")
            print(f"Menor pedido   : R$ {menor_pedido:.2f}")
            print(f"Maior pedido   : R$ {maior_pedido:.2f}")
            print("====================================")

    except Exception as e:

        print(f"\nErro ao consultar faturamento: {e}")

def consultar_pedidos(conn, unidade):

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    CPF,
                    TO_CHAR(DATA_HORA, 'DD/MM/YYYY HH24:MI'),
                    VALOR
                FROM PEDIDO
                WHERE UF = :uf
                  AND CIDADE = :cidade
                  AND EXTRACT(MONTH FROM DATA_HORA) =
                      EXTRACT(MONTH FROM SYSDATE)
                  AND EXTRACT(YEAR FROM DATA_HORA) =
                      EXTRACT(YEAR FROM SYSDATE)
                ORDER BY DATA_HORA DESC
            """, {
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            pedidos = cursor.fetchall()

            print("\n====================================")
            print(" PEDIDOS DO MÊS")
            print("====================================")
            print(f"Loja: {unidade['cidade']} - {unidade['uf']}")
            print("------------------------------------")

            if not pedidos:
                print("Nenhum pedido encontrado.")
                return

            total = 0

            print(
                f"{'CPF':<15} "
                f"{'DATA':<20} "
                f"{'VALOR':>10}"
            )

            print("-" * 50)

            for cpf, data_hora, valor in pedidos:

                total += valor

                print(
                    f"{cpf:<15} "
                    f"{data_hora:<20} "
                    f"R$ {valor:>7.2f}"
                )

            print("-" * 50)
            print(f"Total de pedidos: {len(pedidos)}")
            print(f"Valor movimentado: R$ {total:.2f}")

    except Exception as e:

        print(f"\nErro ao consultar pedidos: {e}")

# ÁREA DE MONITORAMENTO

# min = minimo
def ler_float(mensagem, min=0.0):
    while True:
        entrar = input(mensagem).strip().replace(",", ".")

        try:
            valor = float(entrar)
            if valor < min:
                print(f"o valor deve ser maior ou igual a {min}.")
                continue
            return valor
        
        except ValueError:
            print("Valor não permitido")


def ler_inteiro(mensagem,min=0):
    while True:
        entrar = input(mensagem).strip()
        try:
            valor = int(entrar)
            if valor < min:
                print(f"O valor deve ser maior ou igual a {min}.")
                continue
            return valor
        
        except ValueError:
            print("Digite um numero inteiro valido.")

# ler verdadeiro ou falso
def vf(mensagem):

    while True:
        valor = input(mensagem).strip().upper()
        if valor in ("V","F"):
            return valor
        print("digite V para verdadeiro ou F para falso.")


def data_hora_evento():
    while True:
        entrada = input("data e hora do evento (DD/MM/AAAA HH) ou Enter para a hora atual: ").strip()

        if not entrada:
            return datetime.now().replace(minute=0, second=0, microsecond=0)
        try:

            return datetime.strptime(entrada, "%d/%m/%Y %H")
        except ValueError:

            print("o formato é inválido. tente algo como: 20/06/2026 14")

#consulta pra procurar uma tartaruga pelo codigo de anilha
def buscar_tartaruga(acesso_banco, codigo_anilha):
    acesso_banco.execute(
        """
        SELECT codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico
        FROM Tartaruga
        WHERE codigo_anilha = :codigo_anilha
        """,
        {"codigo_anilha": codigo_anilha},
    )
    return acesso_banco.fetchone()

#busco todos os pesquisadores cadastrados, junto com o nome da pessoa e a formacao
def selecionar_pesquisador(acesso_banco):
    acesso_banco.execute(
        """
        SELECT pq.CPF, p.Nome, pq.formacao
        FROM Pesquisador pq
        JOIN Pessoa p ON p.CPF = pq.CPF
        ORDER BY p.Nome
        """
    )
    pesquisadores = acesso_banco.fetchall()

    if not pesquisadores:
        print("nenhum pesquisador cadastrado")
        return None

    print("\n=== PESQUISADORES ===")
    for indice,(cpf, nome, formacao) in enumerate(pesquisadores,start=1):
        print(f"{indice} - {nome} | CPF: {cpf} | Formação: {formacao or 'Não informada'}")
    print("0 - Cancelar")

    while True:
        try:
            opcao = int(input("escolha o pesquisador responsável: "))
        except ValueError:
            print("digite um número válido")
            continue
        if opcao == 0:
            return None
        if 1 <= opcao<= len(pesquisadores):
            return pesquisadores[opcao - 1][0]
        print("opção invalida")

#verifico se ja existe um evento registrado para a mesma tartaruga na mesma data e hora
def evento_ja_existe(acesso_banco, codigo_anilha, data_hora):
    acesso_banco.execute(
        """
        SELECT classificacao
        FROM Classificacoes
        WHERE codigo_anilha = :codigo_anilha
          AND data_hora = :data_hora
        """,
        {"codigo_anilha": codigo_anilha, "data_hora": data_hora},
    )
    return acesso_banco.fetchone()



'''cadastro uma nova tartaruga verificando se a anilha ja existe,
escolhemos uma espécie e depois fazemos  um INSERT na tabela Tartaruga'''

def cadastrar_tartaruga(conn):
    print("\n=== CADASTRO DE TARTARUGA ===")
    codigo_anilha = input("Código da anilha: ").strip().upper()

    if not codigo_anilha:
        print("O código da anilha é obrigatório.")
        return

    try:
        with conn.cursor() as acesso_banco:
            if buscar_tartaruga(acesso_banco, codigo_anilha):
                print(" ja existe uma tartaruga com esse código de anilha.")
                return

            acesso_banco.execute(
                """
                SELECT nome_cientifico, nivel_de_extincao
                FROM Especie
                ORDER BY nome_cientifico
                """
            )

            especies = acesso_banco.fetchall()

            if not especies:
                print("nenhuma espécie cadastrada. Cadastre uma especie antes da tartaruga")
                return

            print("\n=== ESPÉCIES ===")
            for indice, (nome, nivel) in enumerate(especies, start=1):
                print(f"{indice} - {nome} | Nível de extinção: {nivel or 'Não informado'}")

            while True:
                try:
                    opcao = int(input("Escolha a espécie: "))
                except ValueError:
                    print("digite um numero valido")
                    continue

                if 1<= opcao <= len(especies):
                    nome_cientifico = especies[opcao - 1][0]
                    break
                print("opcao nao permitida")

            peso = ler_float("Peso em kg: ", min=0.0)
            tamanho_casco = ler_float("Tamanho do casco em cm: ", min=0.0)

            while True:
                sexo = input("Sexo (F/M): ").strip().upper()
                if sexo in ("F", "M"):
                    break
                print("Digite F ou M.")

            acesso_banco.execute(
                """
                INSERT INTO Tartaruga (
                    codigo_anilha, peso, tamanho_casco, sexo, nome_cientifico
                )
                VALUES (
                    :codigo_anilha, :peso, :tamanho_casco, :sexo, :nome_cientifico
                )
                """,
                {
                    "codigo_anilha": codigo_anilha,
                    "peso": peso,
                    "tamanho_casco": tamanho_casco,
                    "sexo": sexo,
                    "nome_cientifico": nome_cientifico,
                },
            )

        conn.commit()
        print("tartaruga cadastrada com sucesso")

    except Exception as erro:
        conn.rollback()
        print(f"erro ao cadastrar tartaruga: {erro}")


#registro um evento de resgate ou encalhe de uma tartaruga

def registrar_resgate_encalhe(conn, unidade):

    print("\n=== REGISTRAR RESGATE/ENCALHE ===")
    codigo_anilha = input("Código da anilha: ").strip().upper()

    try:
        with conn.cursor() as acesso_banco:
            tartaruga = buscar_tartaruga(acesso_banco, codigo_anilha)
            if tartaruga is None:
                print("tartaruga não cadastrada")
                return

            cpf_pesquisador = selecionar_pesquisador(acesso_banco)
            if cpf_pesquisador is None:
                return

            data_hora = data_hora_evento()
            evento_existente = evento_ja_existe(acesso_banco, codigo_anilha, data_hora)
            if evento_existente:
                print("já existe um evento para essa tartaruga nessa hora: "f"{evento_existente[0]}.")
                return

            motivo = input("Motivo do resgate/encalhe: ").strip()
            if not motivo:
                print("o motivo é obrigatório.")
                return

            vivo = vf("A tartaruga foi encontrada viva? (V/F): ")

            if vivo == "V":
                reabilitacao = "V"
                print("tartaruga viva será encaminhada para reabilitação")
            else:
                reabilitacao = "F"

            acesso_banco.execute(
                """
                INSERT INTO Classificacoes (
                    codigo_anilha, data_hora, classificacao
                )
                VALUES (
                    :codigo_anilha, :data_hora, 'Resgate'
                )
                """,
                {"codigo_anilha": codigo_anilha, "data_hora": data_hora},
            )

            acesso_banco.execute(
                """
                INSERT INTO Resgate_Encalhe (
                    codigo_anilha, data_hora, UF, cidade, CPF_Pesq,
                    motivo, vivo, reabilitacao
                )
                VALUES (
                    :codigo_anilha, :data_hora, :uf, :cidade, :cpf_pesq,
                    :motivo, :vivo, :reabilitacao
                )
                """,
                {
                    "codigo_anilha": codigo_anilha,
                    "data_hora": data_hora,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"],
                    "cpf_pesq": cpf_pesquisador,
                    "motivo": motivo,
                    "vivo": vivo,
                    "reabilitacao": reabilitacao,
                },
            )

        conn.commit()
        print("Resgate/encalhe registrado com sucesso.")

    except Exception as erro:
        conn.rollback()
        print(f"Erro ao registrar resgate/encalhe: {erro}")


#registro um evento de pesca envolvendo uma tartaruga
def registrar_pesca(conn, unidade):
    print("\n=== REGISTRAR PESCA ===")
    codigo_anilha = input("Código da anilha: ").strip().upper()
    try:
        with conn.cursor() as acesso_banco:

            tartaruga = buscar_tartaruga(acesso_banco,codigo_anilha)

            if tartaruga is None:
                print("tartaruga não cadastrada")
                return
            cpf_pesquisador = selecionar_pesquisador(acesso_banco)
            if cpf_pesquisador is None:
                return
            data_hora = data_hora_evento()
            evento_existente = evento_ja_existe(acesso_banco,codigo_anilha,data_hora)
            if evento_existente:
                print("ja existe um evento para essa tartaruga nessa hora: "f"{evento_existente[0]}.")
                return

            print("\nClasse da pesca")
            print("1 - Monitorada")
            print("2 - Não Monitorada")



            while True:
                opcao = input("Escolha: ").strip()
                if opcao == "1":
                    classe = "Monitorada"
                    break
                if opcao == "2":
                    classe = "Não Monitorada"
                    break
                print("Opção inválida.")
            if classe == "Não Monitorada":
                reabilitacao = "V"
                print("Pesca não monitorada exige reabilitação.")
            else:
                reabilitacao = vf("Foi encaminhada para reabilitação? (V/F): ")


            acesso_banco.execute(
                """
                INSERT INTO Classificacoes (
                    codigo_anilha, data_hora, classificacao
                )
                VALUES (
                    :codigo_anilha, :data_hora, 'Pesca'
                )
                """,
                {"codigo_anilha": codigo_anilha, "data_hora": data_hora},
            )


            acesso_banco.execute(
                """
                INSERT INTO Pesca (
                    codigo_anilha, data_hora, UF, cidade, CPF_Pesq,
                    classe, reabilitacao
                )
                VALUES (
                    :codigo_anilha, :data_hora, :uf, :cidade, :cpf_pesq,
                    :classe, :reabilitacao
                )
                """,
                {
                    "codigo_anilha": codigo_anilha,
                    "data_hora": data_hora,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"],
                    "cpf_pesq": cpf_pesquisador,
                    "classe": classe,
                    "reabilitacao": reabilitacao,
                },
            )

        conn.commit()
        print("Evento de pesca registrado com sucesso")

    except Exception as erro:
        conn.rollback()
        print(f"Erro ao registrar pesca: {erro}")


def registrar_desova(conn,unidade):

    print("\n=== REGISTRAR DESOVA ===")

    codigo_anilha = input("Código da anilha: ").strip().upper()

    try:
        with conn.cursor() as acesso_banco:

            tartaruga = buscar_tartaruga(acesso_banco, codigo_anilha)

            if tartaruga is None:
                print("taartaruga não cadastrada")
                return

            sexo = tartaruga[3]
            if sexo != "F":
                print("somente tartarugas femeas podem realizar desova")
                return

            cpf_pesquisador = selecionar_pesquisador(acesso_banco)
            if cpf_pesquisador is None:
                return

            data_hora = data_hora_evento()
            evento_existente = evento_ja_existe(acesso_banco,codigo_anilha,data_hora)
            if evento_existente:
                print("ja existe um evento para essa tartaruga nessa hora: "f"{evento_existente[0]}.")
                return

            codigo_estaca = input("Código da estaca: ").strip().upper()
            if not codigo_estaca:
                print("O código da estaca é obrigatório.")
                return

            acesso_banco.execute(
                "SELECT 1 FROM Ninho WHERE codigo_estaca = :codigo_estaca",
                {"codigo_estaca": codigo_estaca},
            )
            if acesso_banco.fetchone():
                print("ja existe um ninho com esse código de estaca")
                return

            lat_long = input("Latitude e longitude: ").strip()
            n_ovos = ler_inteiro("Número de ovos: ", min=0)
            n_filhotes = ler_inteiro("Número de filhotes: ", min=0)

            if n_filhotes > n_ovos:
                print("o número de filhotes não pode ser maior que o número de ovos")
                return

            acesso_banco.execute(
                """
                INSERT INTO Ninho (
                    codigo_estaca, lat_long, n_ovos, n_filhotes
                )
                VALUES (
                    :codigo_estaca, :lat_long, :n_ovos, :n_filhotes
                )
                """,
                {
                    "codigo_estaca": codigo_estaca,
                    "lat_long": lat_long or None,
                    "n_ovos": n_ovos,
                    "n_filhotes": n_filhotes,
                },
            )

            acesso_banco.execute(
                """
                INSERT INTO Classificacoes (
                    codigo_anilha, data_hora, classificacao
                )
                VALUES (
                    :codigo_anilha, :data_hora, 'Desova'
                )
                """,
                {"codigo_anilha": codigo_anilha, "data_hora": data_hora},
            )

            acesso_banco.execute(
                """
                INSERT INTO Desova (
                    codigo_anilha, data_hora, UF, cidade, CPF_Pesq, codigo_estaca
                )
                VALUES (
                    :codigo_anilha, :data_hora, :uf, :cidade, :cpf_pesq,
                    :codigo_estaca
                )
                """,
                {
                    "codigo_anilha": codigo_anilha,
                    "data_hora": data_hora,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"],
                    "cpf_pesq": cpf_pesquisador,
                    "codigo_estaca": codigo_estaca,
                },
            )

        conn.commit()
        print("desova e ninho registrados com sucesso!")

    except Exception as erro:
        conn.rollback()
        print(f"errro ao registrar desova: {erro}")


def consultar_historico_tartaruga(conn):

    print("\n=== HISTÓRICO DA TARTARUGA ===")

    codigo_anilha = input("Código da anilha: ").strip().upper()

    try:
        with conn.cursor() as acesso_banco:


            acesso_banco.execute(
                """
                SELECT t.codigo_anilha, t.peso, t.tamanho_casco, t.sexo,
                       t.nome_cientifico, e.nivel_de_extincao
                FROM Tartaruga t
                JOIN Especie e ON e.nome_cientifico = t.nome_cientifico
                WHERE t.codigo_anilha = :codigo_anilha
                """,
                {"codigo_anilha": codigo_anilha},
            )
            tartaruga = acesso_banco.fetchone()


            if tartaruga is None:
                print("tartaruga não cadastrada")
                return

            acesso_banco.execute(
                """
                SELECT tipo, data_hora, UF, cidade, pesquisador, detalhes
                FROM (
                    SELECT 'RESGATE/ENCALHE' AS tipo, r.data_hora, r.UF, r.cidade,
                           p.Nome AS pesquisador,
                           'Motivo: ' || NVL(r.motivo, 'Não informado') ||
                           ' | Viva: ' || NVL(r.vivo, '-') ||
                           ' | Reabilitação: ' || NVL(r.reabilitacao, '-') AS detalhes
                    FROM Resgate_Encalhe r
                    JOIN Pessoa p ON p.CPF = r.CPF_Pesq
                    WHERE r.codigo_anilha = :codigo_anilha

                    UNION ALL

                    SELECT 'PESCA' AS tipo, pc.data_hora, pc.UF, pc.cidade,
                           p.Nome AS pesquisador,
                           'Classe: ' || NVL(pc.classe, 'Não informada') ||
                           ' | Reabilitação: ' || NVL(pc.reabilitacao, '-') AS detalhes
                    FROM Pesca pc
                    JOIN Pessoa p ON p.CPF = pc.CPF_Pesq
                    WHERE pc.codigo_anilha = :codigo_anilha

                    UNION ALL

                    SELECT 'DESOVA' AS tipo, d.data_hora, d.UF, d.cidade,
                           p.Nome AS pesquisador,
                           'Estaca: ' || d.codigo_estaca ||
                           ' | Ovos: ' || TO_CHAR(NVL(n.n_ovos, 0)) ||
                           ' | Filhotes: ' || TO_CHAR(NVL(n.n_filhotes, 0)) AS detalhes
                    FROM Desova d
                    JOIN Pessoa p ON p.CPF = d.CPF_Pesq
                    JOIN Ninho n ON n.codigo_estaca = d.codigo_estaca
                    WHERE d.codigo_anilha = :codigo_anilha
                )
                ORDER BY data_hora DESC
                """,
                {"codigo_anilha": codigo_anilha},
            )
            eventos = acesso_banco.fetchall()

        print("\n====================================")
        print(f"Anilha........: {tartaruga[0]}")
        print(f"Espécie.......: {tartaruga[4]}")
        print(f"Ameaça........: {tartaruga[5] or 'Não informada'}")
        print(f"Sexo..........: {tartaruga[3]}")
        print(f"Peso..........: {tartaruga[1] or 0} kg")
        print(f"Casco.........: {tartaruga[2] or 0} cm")
        print("====================================")

        if not eventos:
            print("nenhum evento registrado para essa tartaruga")
            return

        for tipo, data_hora, uf, cidade, pesquisador, detalhes in eventos:
            print(f"\n{tipo} - {data_hora.strftime('%d/%m/%Y %H:%M')}")
            print(f"Local.........: {uf} - {cidade}")
            print(f"Pesquisador...: {pesquisador}")
            print(f"Detalhes......: {detalhes}")

    except Exception as erro:
        print(f"Erro ao consultar histórico: {erro}")


def consultar_estatisticas_area(conn, unidade):
    try:
        with conn.cursor() as acesso_banco:
            parametros = {"uf": unidade["uf"], "cidade": unidade["cidade"]}

            acesso_banco.execute(
                """
                SELECT COUNT(*),
                       SUM(CASE WHEN vivo = 'V' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN reabilitacao = 'V' THEN 1 ELSE 0 END)
                FROM Resgate_Encalhe
                WHERE UF = :uf AND cidade = :cidade
                """,
                parametros,
            )
            resgates, vivos, reabilitados_resgate = acesso_banco.fetchone()

            acesso_banco.execute(
                """
                SELECT COUNT(*),
                       SUM(CASE WHEN classe = 'Monitorada' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN classe = 'Não Monitorada' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN reabilitacao = 'V' THEN 1 ELSE 0 END)
                FROM Pesca
                WHERE UF = :uf AND cidade = :cidade
                """,
                parametros,
            )
            pescas, monitoradas, nao_monitoradas, reabilitados_pesca = acesso_banco.fetchone()

            acesso_banco.execute(
                """
                SELECT COUNT(*), NVL(SUM(n.n_ovos), 0), NVL(SUM(n.n_filhotes), 0)
                FROM Desova d
                JOIN Ninho n ON n.codigo_estaca = d.codigo_estaca
                WHERE d.UF = :uf AND d.cidade = :cidade
                """,
                parametros,
            )
            desovas, ovos, filhotes = acesso_banco.fetchone()

            acesso_banco.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT codigo_anilha FROM Resgate_Encalhe
                    WHERE UF = :uf AND cidade = :cidade
                    UNION
                    SELECT codigo_anilha FROM Pesca
                    WHERE UF = :uf AND cidade = :cidade
                    UNION
                    SELECT codigo_anilha FROM Desova
                    WHERE UF = :uf AND cidade = :cidade
                )
                """,
                parametros,
            )
            tartarugas = acesso_banco.fetchone()[0]

            acesso_banco.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT CPF_Pesq FROM Resgate_Encalhe
                    WHERE UF = :uf AND cidade = :cidade
                    UNION
                    SELECT CPF_Pesq FROM Pesca
                    WHERE UF = :uf AND cidade = :cidade
                    UNION
                    SELECT CPF_Pesq FROM Desova
                    WHERE UF = :uf AND cidade = :cidade
                )
                """,
                parametros,
            )
            pesquisadores = acesso_banco.fetchone()[0]

        resgates = resgates or 0
        vivos = vivos or 0
        reabilitados_resgate = reabilitados_resgate or 0
        pescas = pescas or 0
        monitoradas = monitoradas or 0
        nao_monitoradas = nao_monitoradas or 0
        reabilitados_pesca = reabilitados_pesca or 0
        desovas = desovas or 0
        ovos = ovos or 0
        filhotes = filhotes or 0

        taxa_reabilitacao = (100 * reabilitados_resgate / resgates if resgates else 0)
        taxa_eclosao = 100 * filhotes / ovos if ovos else 0
        total_eventos = resgates + pescas + desovas

        print("\n====================================")
        print(" ESTATÍSTICAS DA ÁREA")
        print("====================================")
        print(f"Área.................: {unidade['uf']} - {unidade['cidade']}")
        print(f"Total de eventos.....: {total_eventos}")
        print(f"Tartarugas distintas.: {tartarugas}")
        print(f"Pesquisadores........: {pesquisadores}")
        print("------------------------------------")
        print(f"Resgates..............: {resgates}")
        print(f"Encontradas vivas.....: {vivos}")
        print(f"Reabilitadas..........: {reabilitados_resgate}")
        print(f"Taxa de reabilitação..: {taxa_reabilitacao:.2f}%")
        print("------------------------------------")
        print(f"Pescas................: {pescas}")
        print(f"Monitoradas...........: {monitoradas}")
        print(f"Não monitoradas.......: {nao_monitoradas}")
        print(f"Reabilitações pesca...: {reabilitados_pesca}")
        print("------------------------------------")
        print(f"Desovas...............: {desovas}")
        print(f"Ovos..................: {ovos}")
        print(f"Filhotes..............: {filhotes}")
        print(f"Taxa de eclosão.......: {taxa_eclosao:.2f}%")
        print("====================================")

    except Exception as erro:
        print(f"erro ao consultar estatísticas: {erro}")

# === funções museu ===
# Função para vender um ingresso
def vender_ingresso(conn, unidade):
    try:
        cpf = input("\nCPF do visitante: ").strip()

        if not cpf.isdigit():
            print("CPF deve conter apenas números.")
            return

        with conn.cursor() as cursor:

            # Verifica se a pessoa existe
            cursor.execute("""
                SELECT NOME
                FROM PESSOA
                WHERE CPF = :cpf
            """, {"cpf": cpf})

            resultado = cursor.fetchone()

            if resultado is None:
                print("\nCliente não encontrado.")
                print("=== NOVO CADASTRO ===")

                nome = input("Nome: ").strip()

                data_nasc = input("Data de nascimento (DD/MM/YYYY): ").strip()

                while True:
                    print("\nPrioridade por lei")
                    print("1 - Nenhuma")
                    print("2 - Estudante")
                    print("3 - Idoso")
                    print("4 - Gestante")

                    opc = input("Opção: ").strip()

                    if opc in ["1", "2", "3", "4"]:
                        break

                    print("Opção inválida.")

                prioridade = None

                if opc == "2":
                    prioridade = "Estudante"
                elif opc == "3":
                    prioridade = "Idoso"
                elif opc == "4":
                    prioridade = "Gestante"

                cursor.execute("""
                    INSERT INTO PESSOA (
                        CPF,
                        NOME,
                        DATA_NASCIM,
                        FUNCAO,
                        PRIORIDADE_LEI
                    )
                    VALUES (
                        :cpf,
                        :nome,
                        TO_DATE(:data_nasc,'DD/MM/YYYY'),
                        NULL,
                        :prioridade
                    )
                """, {
                    "cpf": cpf,
                    "nome": nome,
                    "data_nasc": data_nasc,
                    "prioridade": prioridade
                })

                print("\nCliente cadastrado com sucesso.")

            # pessoa existe
            else:
                nome = resultado[0]

                cursor.execute("""
                    SELECT PRIORIDADE_LEI
                    FROM PESSOA
                    WHERE CPF = :cpf
                """, {"cpf": cpf})

                prioridade = cursor.fetchone()[0]

            # Verifica se já existe relacionamento VISITA
            cursor.execute("""
                SELECT 1
                FROM VISITA
                WHERE CPF = :cpf
                  AND UF = :uf
                  AND CIDADE = :cidade
            """, {
                "cpf": cpf,
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            # Não existe o relacionamento VISITA -> registra a visita
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO VISITA (
                        CPF,
                        UF,
                        CIDADE
                    )
                    VALUES (
                        :cpf,
                        :uf,
                        :cidade
                    )
                """, {
                    "cpf": cpf,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"]
                })

            # Agora que já tem certeza da existência da visita, cadastro o ingresso 

            # se pessoa é idosa, ganha gratuidade
            if prioridade == 'Idoso':
                categoria = 'Gratuidade'
                valor = 0.00

            # se pessoa tem alguma prioridade por lei, recebe meia entrada
            elif prioridade != None:
                categoria = 'Meia'
                valor = 20.00

            # pessoa não tem prioridade
            else:
                categoria = 'Inteira'
                valor = 40.00

            # Cadastro do ingresso
            cursor.execute("""
                INSERT INTO INGRESSO (
                    CPF,
                    UF,
                    CIDADE,
                    DATA_HORA,
                    VALOR,
                    CATEGORIA
                )
                VALUES (
                    :cpf,
                    :uf,
                    :cidade,
                    SYSDATE,
                    :valor,
                    :categoria
                )
            """, {
                "cpf": cpf,
                "uf": unidade["uf"],
                "cidade": unidade["cidade"],
                "valor": valor,
                "categoria": categoria
            })

        conn.commit()

        momento = datetime.now()

        print("\n====================================")
        print("          PROJETO TAMAR")
        print("====================================")
        print("Ingresso registrado com sucesso")
        print("------------------------------------")
        print(f"Cliente......: {nome}")
        print(f"CPF..........: {cpf}")

        if prioridade:
            print(f"Prioridade...: {prioridade}")
        else:
            print("Prioridade...: Nenhuma")

        print(
            f"Museu.........: "
            f"{unidade['uf']} - {unidade['cidade']}"
        )

        print(f"Valor........: R$ {valor:.2f}")

        print(
            "Data/Hora....: "
            f"{momento.strftime('%d/%m/%Y %H:%M:%S')}"
        )

        print("====================================")

    except Exception as e:
        conn.rollback()
        print("\nErro ao registrar pedido.")
        print(e)

# Função para consultar faturamento do museu
def consultar_faturamento_museu(conn, unidade):
    try:
        with conn.cursor() as cursor:

            # pegar todos os ingressos (e estatísticas)
            cursor.execute("""
                SELECT
                    COUNT(*) AS quantidade_ingressos,
                    NVL(SUM(VALOR), 0) AS faturamento_total,
                    NVL(SUM(CASE WHEN CATEGORIA = 'Gratuidade' THEN 1 ELSE 0 END), 0) AS qtd_gratuidade,
                    NVL(SUM(CASE WHEN CATEGORIA = 'Meia' THEN 1 ELSE 0 END), 0) AS qtd_meia,
                    NVL(SUM(CASE WHEN CATEGORIA = 'Inteira' THEN 1 ELSE 0 END), 0) AS qtd_inteira
                FROM INGRESSO
                WHERE UF = :uf
                  AND CIDADE = :cidade
                  AND EXTRACT(MONTH FROM DATA_HORA) =
                      EXTRACT(MONTH FROM SYSDATE)
                  AND EXTRACT(YEAR FROM DATA_HORA) =
                      EXTRACT(YEAR FROM SYSDATE)
            """, {
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            resultado = cursor.fetchone()

            qtd_ingressos = resultado[0] # qtd de ingressos vendidos
            faturamento = resultado[1] # valor do faturamento total
            qtd_gratuidade = resultado[2] # qtd de ingressos gratis vendidos
            qtd_meia = resultado[3] # qtd de meia entrada vendidas
            qtd_inteira = resultado[4] # qtd de inteiras vendidas

            print("\n====================================")
            print(" FATURAMENTO MENSAL")
            print("====================================")
            print(f"Museu: {unidade['cidade']} - {unidade['uf']}")
            print("------------------------------------")
            print(f"Ingressos no mês: {qtd_ingressos}")
            print(f"Faturamento: R$ {faturamento:.2f}")
            print(f"Quantidade de ingressos gratuitos vendidos: {qtd_gratuidade}")
            print(f"Quantidade de meia-entradas vendidas: {qtd_meia}")
            print(f"Quantidade de inteiras vendidas: {qtd_inteira}")
            print("====================================")

    except Exception as e:
        print(f"\nErro ao consultar faturamento: {e}")

# Função para consultar visitantes do dia
def consultar_visitantes_dia(conn, unidade):
    try:
        with conn.cursor() as cursor:
            # entrar com a data que deseja-se fazer a consulta
            data = input("Data (DD/MM/YYYY): ").strip()

            # selecionar os ingressos do dia
            cursor.execute("""
                SELECT
                    CPF,
                    TO_CHAR(DATA_HORA, 'DD/MM/YYYY HH24:MI'),
                    CATEGORIA,
                    VALOR
                FROM INGRESSO
                WHERE UF = :uf
                  AND CIDADE = :cidade
                  AND TRUNC(DATA_HORA) = TO_DATE(:data, 'DD/MM/YYYY')
                ORDER BY DATA_HORA DESC
            """, {
                "uf": unidade["uf"],
                "cidade": unidade["cidade"],
                "data": data
            })

            ingressos = cursor.fetchall()

            print("\n====================================")
            print(f" VISITANTES DO DIA {data}")
            print("====================================")
            print(f"Museu: {unidade['cidade']} - {unidade['uf']}")
            print("------------------------------------")

            if not ingressos:
                print("Nenhum visitante encontrado.")
                return

            total = 0

            # configuração para mostrar os resultados
            print(
                f"{'CPF':<15} "
                f"{'DATA':<20} "
                f"{'VALOR':>11}"
            )
            print("-" * 50)

            for cpf, data_hora, categoria, valor in ingressos:
                total += valor

                print(
                    f"{cpf:<15} "
                    f"{data_hora:<20} "
                    f"{categoria:>11}"
                )

            print("-" * 50)
            print(f"Total de ingressos: {len(ingressos)}")
            print(f"Valor movimentado: R$ {total:.2f}")

    except Exception as e:
        print(f"\nErro ao consultar ingressos: {e}")

# ÁREA DE MONITORAMENTO
def menu_monitoramento(conn, unidade):
    while True:
        print("\n====================================")
        print(" ÁREA DE MONITORAMENTO")
        print("====================================")
        print(f"UF: {unidade['uf']}")
        print(f"Cidade: {unidade['cidade']}")
        print("------------------------------------")
        print("1 - Cadastrar tartaruga")
        print("2 - Registrar resgate/encalhe")
        print("3 - Registrar pesca")
        print("4 - Registrar desova")
        print("5 - Consultar histórico de uma tartaruga")
        print("6 - Consultar estatísticas da área")
        print("0 - Voltar")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_tartaruga(conn)
        elif opcao == "2":
            registrar_resgate_encalhe(conn, unidade)
        elif opcao == "3":
            registrar_pesca(conn, unidade)
        elif opcao == "4":
            registrar_desova(conn, unidade)
        elif opcao == "5":
            consultar_historico_tartaruga(conn)
        elif opcao == "6":
            consultar_estatisticas_area(conn, unidade)
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")

# MUSEU
def menu_museu(conn, unidade):

    while True:

        print("\n====================================")
        print(" MUSEU")
        print("====================================")
        print(f"UF: {unidade['uf']}")
        print(f"Cidade: {unidade['cidade']}")
        print("------------------------------------")
        print("1 - Vender ingresso")
        print("2 - Consultar faturamento")
        print("3 - Consultar visitantes do dia")
        print("0 - Voltar")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            vender_ingresso(conn, unidade)

        elif opcao == "2":
            consultar_faturamento_museu(conn, unidade)

        elif opcao == "3":
            consultar_visitantes_dia(conn, unidade)

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")

# LOJA
def menu_loja(conn, unidade):

    while True:

        print("\n====================================")
        print(" LOJA")
        print("====================================")
        print(f"UF: {unidade['uf']}")
        print(f"Cidade: {unidade['cidade']}")
        print("------------------------------------")
        print("1 - Registrar pedido")
        print("2 - Consultar faturamento do mês atual")
        print("3 - Consultar pedidos do mês atual")
        print("0 - Voltar")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            registrar_pedido(conn, unidade)

        elif opcao == "2":
            consultar_faturamento_loja(conn, unidade)

        elif opcao == "3":
            consultar_pedidos(conn, unidade)

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")


# MENU PRINCIPAL
def menu_principal():

    print("\n====================================")
    print(" SISTEMA PROJETO TAMAR")
    print("====================================")
    print("1 - Área de Monitoramento")
    print("2 - Museu")
    print("3 - Loja")
    print("4 - Cadastrar nova unidade")
    print("5 - UMA DAS CONSULTAS DO RELATORIO")
    print("0 - Sair")


# MAIN
def main():

    conn = conectar()

    if conn is None:
        print("Não foi possível conectar ao banco.")
        return

    try:

        while True:

            menu_principal()

            opcao = input("\nEscolha uma opção: ")

            if opcao == "1":

                unidade = selecionar_unidade(
                    conn,
                    "AREA_DE_MONITORAMENTO",
                    "Área de Monitoramento"
                )

                if unidade:
                    menu_monitoramento(conn, unidade)

            elif opcao == "2":

                unidade = selecionar_unidade(
                    conn,
                    "MUSEU",
                    "Museu"
                )

                if unidade:
                    menu_museu(conn, unidade)

            elif opcao == "3":

                unidade = selecionar_unidade(
                    conn,
                    "LOJA",
                    "Loja"
                )

                if unidade:
                    menu_loja(conn, unidade)

            elif opcao == "4":

                print("\nAcesso negado.")
                print("Somente usuários com credencial de gerente podem cadastrar novas unidades.")

            elif opcao == "5":
                print("\nFuncionalidade em desenvolvimento.")

            elif opcao == "0":

                print("\nEncerrando sistema...")
                break

            else:

                print("Opção inválida.")

    except KeyboardInterrupt:

        print("\nSistema interrompido pelo usuário.")

    except Exception as e:

        print(f"\nErro inesperado: {e}")

        try:
            conn.rollback()
        except:
            pass

    finally:

        conn.close()
        print("Conexão encerrada.")


if __name__ == "__main__":
    main()
