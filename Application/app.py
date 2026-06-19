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
        print("5 - Consultar tartaruga")
        print("0 - Voltar")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            print("Funcionalidade em desenvolvimento.")

        elif opcao == "2":
            print("Funcionalidade em desenvolvimento.")

        elif opcao == "3":
            print("Funcionalidade em desenvolvimento.")

        elif opcao == "4":
            print("Funcionalidade em desenvolvimento.")

        elif opcao == "5":
            print("Funcionalidade em desenvolvimento.")

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
            print("Funcionalidade em desenvolvimento.")

        elif opcao == "2":
            print("Funcionalidade em desenvolvimento.")

        elif opcao == "3":
            print("Funcionalidade em desenvolvimento.")

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