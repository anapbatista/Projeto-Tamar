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

# funções area de monitoramento

# modularização
def obter_pesquisador(cursor):
    """Solicita, valida e verifica a existência do pesquisador no banco."""
    cpf_pesq = input("CPF do Pesquisador Responsável: ").strip().replace(".", "").replace("-", "")
    if not cpf_pesq.isdigit() or len(cpf_pesq) != 11:
        print("[Erro] CPF do pesquisador deve conter exatamente 11 dígitos numéricos.")
        return None

    cursor.execute("SELECT 1 FROM PESQUISADOR WHERE CPF = :cpf", {"cpf": cpf_pesq})
    if cursor.fetchone() is None:
        print("\n[Aviso] Pesquisador não encontrado na base de dados.")
        print("Operação Cancelada: O pesquisador precisa ser cadastrado previamente pelo gerente da base.")
        return None
        
    return cpf_pesq

def obter_ou_cadastrar_tartaruga(cursor, prompt="\nCódigo da anilha da tartaruga: "):
    """Busca a tartaruga e aciona o fluxo de cadastro caso ela não exista."""
    while True:
        codigo_anilha = input(prompt).strip().upper()
        if not codigo_anilha:
            print("[Erro] O código da anilha não pode ser vazio.")
            continue

        cursor.execute("""
            SELECT PESO, TAMANHO_CASCO, SEXO, NOME_CIENTIFICO 
            FROM TARTARUGA WHERE CODIGO_ANILHA = :codigo
        """, {"codigo": codigo_anilha})
        
        resultado = cursor.fetchone()

        if resultado is not None:
            print(f"\nTartaruga identificada: Espécie {resultado[3]}")
            return codigo_anilha

        print("\n[Aviso] Tartaruga não encontrada.")
        print("1 - Digitar o código da anilha novamente")
        print("2 - Cadastrar como uma nova tartaruga")
        print("0 - Cancelar operação")
        
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            continue
        elif opcao == "2":
            print("\n=== NOVO CADASTRO DE TARTARUGA ===")
            while True:
                nome_especie = input("Nome Científico da Espécie: ").strip()
                cursor.execute("SELECT 1 FROM ESPECIE WHERE NOME_CIENTIFICO = :nome", {"nome": nome_especie})
                if cursor.fetchone() is not None: break
                print("[Erro] Espécie não cadastrada no sistema. Digite uma espécie válida.")

            while True:
                sexo = input("Sexo (M/F): ").strip().upper()
                if sexo in ["M", "F"]: break
                print("[Erro] Entrada inválida. Digite apenas M ou F.")

            while True:
                try:
                    peso = float(input("Peso (kg): ").replace(",", "."))
                    if peso > 0: break
                    print("[Erro] O peso deve ser maior que zero.")
                except ValueError:
                    print("[Erro] Digite um valor numérico válido.")

            while True:
                try:
                    tamanho = float(input("Tamanho do Casco (cm): ").replace(",", "."))
                    if tamanho > 0: break
                    print("[Erro] O tamanho deve ser maior que zero.")
                except ValueError:
                    print("[Erro] Digite um valor numérico válido.")

            cursor.execute("""
                INSERT INTO TARTARUGA (CODIGO_ANILHA, PESO, TAMANHO_CASCO, SEXO, NOME_CIENTIFICO)
                VALUES (:codigo, :peso, :tamanho, :sexo, :especie)
            """, {
                "codigo": codigo_anilha, "peso": peso, "tamanho": tamanho, 
                "sexo": sexo, "especie": nome_especie
            })
            print("\nTartaruga cadastrada com sucesso.")
            return codigo_anilha
            
        elif opcao == "0":
            print("\nOperação cancelada pelo usuário.")
            return None
        else:
            print("[Aviso] Opção inválida. Retornando à busca do código.")

def obter_input_vf(mensagem):
    """Função utilitária para capturar e validar entradas booleanas (V, F ou Nulo)."""
    while True:
        valor = input(mensagem).strip().upper()
        if valor in ["V", "F", ""]:
            return valor if valor != "" else None
        print("[Erro] Entrada inválida. Digite apenas V, F ou deixe em branco.")

def registrar_resgate_encalhe(conn, unidade):
    try:
        print("\n=== REGISTRAR RESGATE / ENCALHE ===")
        print(f"Área de Monitoramento: {unidade['uf']} - {unidade['cidade']}")
        
        with conn.cursor() as cursor:
            cpf_pesq = obter_pesquisador(cursor)
            if not cpf_pesq: return

            codigo_anilha = obter_ou_cadastrar_tartaruga(cursor)
            if not codigo_anilha: return

            motivo = input("\nMotivo do resgate/encalhe (Pressione Enter para nulo): ").strip()
            motivo = motivo if motivo != "" else None

            vivo = obter_input_vf("A tartaruga foi encontrada viva? (V/F ou Enter para nulo): ")
            reabilitacao = obter_input_vf("Será encaminhada para reabilitação? (V/F ou Enter para nulo): ")

            if vivo == "V" and reabilitacao != "V":
                print("\n[Nota do Sistema] Conforme protocolo do Projeto Tamar, tartarugas vivas resgatadas devem ir para reabilitação.")
                reabilitacao = "V"

            cursor.execute("""
                INSERT INTO CLASSIFICACOES (CODIGO_ANILHA, DATA_HORA, CLASSIFICACAO)
                VALUES (:codigo, TRUNC(SYSDATE, 'HH24'), 'Resgate')
            """, {"codigo": codigo_anilha})

            cursor.execute("""
                INSERT INTO RESGATE_ENCALHE (CODIGO_ANILHA, DATA_HORA, UF, CIDADE, CPF_PESQ, MOTIVO, VIVO, REABILITACAO)
                VALUES (:codigo, TRUNC(SYSDATE, 'HH24'), :uf, :cidade, :cpf_pesq, :motivo, :vivo, :reabilitacao)
            """, {
                "codigo": codigo_anilha, "uf": unidade["uf"], "cidade": unidade["cidade"],
                "cpf_pesq": cpf_pesq, "motivo": motivo, "vivo": vivo, "reabilitacao": reabilitacao
            })

        conn.commit()
        
        print("\n====================================")
        print("         PROJETO TAMAR")
        print("====================================")
        print("Resgate/Encalhe registrado com sucesso")
        print("------------------------------------")
        print(f"Anilha Tartaruga: {codigo_anilha}")
        print(f"Pesquisador CPF.: {cpf_pesq}")
        print(f"Data/Hora Base..: {datetime.now().strftime('%d/%m/%Y %H:00:00')}")
        print("====================================")

    except Exception as e:
        conn.rollback()
        print("\nErro ao registrar o evento de resgate/encalhe.")
        print(e)

def registrar_pesca(conn, unidade):
    try:
        print("\n=== REGISTRAR EVENTO DE PESCA ===")
        print(f"Área de Monitoramento: {unidade['uf']} - {unidade['cidade']}")
        
        with conn.cursor() as cursor:
            cpf_pesq = obter_pesquisador(cursor)
            if not cpf_pesq: return

            codigo_anilha = obter_ou_cadastrar_tartaruga(cursor)
            if not codigo_anilha: return

            while True:
                classe = input("\nClasse da Pesca (Monitorada / Não Monitorada ou Enter): ").strip()
                if classe in ["Monitorada", "Não Monitorada", ""]: break
                print("[Erro] Entrada inválida. Digite 'Monitorada', 'Não Monitorada' ou deixe vazio.")
            classe = classe if classe != "" else None

            reabilitacao = obter_input_vf("Foi encaminhada para reabilitação? (V/F ou Enter para nulo): ")

            if classe == "Não Monitorada" and reabilitacao != "V":
                print("\n[Nota do Sistema] Capturas acidentais locais exigem reabilitação preventiva.")
                reabilitacao = "V"

            cursor.execute("""
                INSERT INTO CLASSIFICACOES (CODIGO_ANILHA, DATA_HORA, CLASSIFICACAO)
                VALUES (:codigo, TRUNC(SYSDATE, 'HH24'), 'Pesca')
            """, {"codigo": codigo_anilha})

            cursor.execute("""
                INSERT INTO PESCA (CODIGO_ANILHA, DATA_HORA, UF, CIDADE, CPF_PESQ, CLASSE, REABILITACAO)
                VALUES (:codigo, TRUNC(SYSDATE, 'HH24'), :uf, :cidade, :cpf_pesq, :classe, :reabilitacao)
            """, {
                "codigo": codigo_anilha, "uf": unidade["uf"], "cidade": unidade["cidade"],
                "cpf_pesq": cpf_pesq, "classe": classe, "reabilitacao": reabilitacao
            })

        conn.commit()

        print("\n====================================")
        print("         PROJETO TAMAR")
        print("====================================")
        print("Evento de Pesca registrado com sucesso")
        print("------------------------------------")
        print(f"Anilha Tartaruga: {codigo_anilha}")
        print(f"Pesquisador CPF.: {cpf_pesq}")
        print(f"Data/Hora Base..: {datetime.now().strftime('%d/%m/%Y %H:00:00')}")
        print("====================================")

    except Exception as e:
        conn.rollback()
        print("\nErro ao registrar o evento de pesca.")
        print(e)

def registrar_desova(conn, unidade):
    try:
        print("\n=== REGISTRAR EVENTO DE DESOVA ===")
        print(f"Área de Monitoramento: {unidade['uf']} - {unidade['cidade']}")
        
        with conn.cursor() as cursor:
            cpf_pesq = obter_pesquisador(cursor)
            if not cpf_pesq: return

            codigo_anilha = obter_ou_cadastrar_tartaruga(cursor, "\nCódigo da anilha da tartaruga (Fêmea): ")
            if not codigo_anilha: return

            print("\n=== INFORMAÇÕES DO NINHO ASSOCIADO ===")
            while True:
                codigo_estaca = input("Código da Estaca (Obrigatório - ex: EST-102): ").strip().upper()
                if codigo_estaca:
                    cursor.execute("SELECT 1 FROM NINHO WHERE CODIGO_ESTACA = :estaca", {"estaca": codigo_estaca})
                    if cursor.fetchone() is None: break
                    print("[Erro] Este código de estaca já está cadastrado no sistema. Escolha outro.")
                else:
                    print("[Erro] O código da estaca não pode ser vazio.")

            lat_long = input("Coordenadas Geográficas (Latitude/Longitude ou Enter): ").strip()
            lat_long = lat_long if lat_long != "" else None

            while True:
                n_ovos_input = input("Quantidade de ovos (Inteiro ou Enter): ").strip()
                if n_ovos_input == "":
                    n_ovos = None
                    break
                if n_ovos_input.isdigit() and int(n_ovos_input) >= 0:
                    n_ovos = int(n_ovos_input)
                    break
                print("[Erro] Entrada inválida. Digite um número inteiro.")

            while True:
                n_filhotes_input = input("Quantidade de filhotes nascidos (Inteiro ou Enter): ").strip()
                if n_filhotes_input == "":
                    n_filhotes = None
                    break
                if n_filhotes_input.isdigit() and int(n_filhotes_input) >= 0:
                    n_filhotes = int(n_filhotes_input)
                    if n_ovos is not None and n_filhotes > n_ovos:
                        print("[Erro] Filhotes não podem ser maiores que o total de ovos.")
                        continue
                    break
                print("[Erro] Entrada inválida. Digite um número inteiro.")

            cursor.execute("""
                INSERT INTO NINHO (CODIGO_ESTACA, LAT_LONG, N_OVOS, N_FILHOTES)
                VALUES (:codigo_estaca, :lat_long, :n_ovos, :n_filhotes)
            """, {"codigo_estaca": codigo_estaca, "lat_long": lat_long, "n_ovos": n_ovos, "n_filhotes": n_filhotes})

            cursor.execute("""
                INSERT INTO CLASSIFICACOES (CODIGO_ANILHA, DATA_HORA, CLASSIFICACAO)
                VALUES (:codigo, TRUNC(SYSDATE, 'HH24'), 'Desova')
            """, {"codigo": codigo_anilha})

            cursor.execute("""
                INSERT INTO DESOVA (CODIGO_ANILHA, DATA_HORA, UF, CIDADE, CPF_PESQ, CODIGO_ESTACA)
                VALUES (:codigo, TRUNC(SYSDATE, 'HH24'), :uf, :cidade, :cpf_pesq, :codigo_estaca)
            """, {
                "codigo": codigo_anilha, "uf": unidade["uf"], "cidade": unidade["cidade"],
                "cpf_pesq": cpf_pesq, "codigo_estaca": codigo_estaca
            })

        conn.commit()

        print("\n====================================")
        print("         PROJETO TAMAR")
        print("====================================")
        print("Evento de Desova registrado com sucesso")
        print("------------------------------------")
        print(f"Anilha Tartaruga: {codigo_anilha}")
        print(f"Código Estaca...: {codigo_estaca}")
        print(f"Data/Hora Base..: {datetime.now().strftime('%d/%m/%Y %H:00:00')}")
        print("====================================")

    except Exception as e:
        conn.rollback()
        print("\nErro ao registrar o evento de desova.")
        print(e)

def consultar_historico_tartaruga(conn):
    """
    Busca todas as ocorrências de uma tartaruga específica em todas as tabelas de eventos.
    A busca é global (não depende da unidade atual) para mostrar a movimentação do animal.
    """
    try:
        print("\n=== CONSULTAR HISTÓRICO DE TARTARUGA ===")
        codigo_anilha = input("Digite o Código da Anilha: ").strip().upper()
        
        if not codigo_anilha:
            print("[Erro] O código da anilha não pode ser vazio.")
            return

        with conn.cursor() as cursor:
            # 1. Verifica se a tartaruga existe e pega a espécie
            cursor.execute("""
                SELECT NOME_CIENTIFICO, SEXO 
                FROM TARTARUGA 
                WHERE CODIGO_ANILHA = :codigo
            """, {"codigo": codigo_anilha})
            
            tartaruga = cursor.fetchone()
            
            if tartaruga is None:
                print("\n[Aviso] Tartaruga não encontrada na base de dados.")
                return
                
            especie, sexo = tartaruga[0], tartaruga[1]
            
            # 2. Busca o histórico unificado e ordenado cronologicamente
            cursor.execute("""
                SELECT TO_CHAR(DATA_HORA, 'DD/MM/YYYY HH24:MI') AS DATA_FORMATADA, 
                       TIPO_EVENTO, 
                       LOCALIDADE
                FROM (
                    SELECT DATA_HORA, 'Resgate/Encalhe' AS TIPO_EVENTO, CIDADE || ' - ' || UF AS LOCALIDADE 
                    FROM RESGATE_ENCALHE WHERE CODIGO_ANILHA = :codigo
                    UNION ALL
                    SELECT DATA_HORA, 'Pesca Acidental' AS TIPO_EVENTO, CIDADE || ' - ' || UF AS LOCALIDADE 
                    FROM PESCA WHERE CODIGO_ANILHA = :codigo
                    UNION ALL
                    SELECT DATA_HORA, 'Desova Registrada' AS TIPO_EVENTO, CIDADE || ' - ' || UF AS LOCALIDADE 
                    FROM DESOVA WHERE CODIGO_ANILHA = :codigo
                )
                ORDER BY DATA_HORA ASC
            """, {"codigo": codigo_anilha})
            
            eventos = cursor.fetchall()
            
        # 3. Exibição dos resultados formatados
        print("\n=======================================================")
        print(f" HISTÓRICO: {codigo_anilha} | {especie} ({sexo})")
        print("=======================================================")
        
        if not eventos:
            print("Nenhum evento de campo registrado para este animal.")
        else:
            print(f"{'DATA / HORA':<18} | {'TIPO DE EVENTO':<20} | {'LOCALIDADE'}")
            print("-" * 55)
            for ev in eventos:
                print(f"{ev[0]:<18} | {ev[1]:<20} | {ev[2]}")
        print("=======================================================")

    except Exception as e:
        print("\n[Erro] Falha ao consultar o histórico.")
        print(e)

def consultar_estatisticas_area(conn, unidade):
    """
    Gera um relatório sintético da área de monitoramento em que o usuário está logado no momento.
    """
    try:
        print(f"\n=== ESTATÍSTICAS DA BASE: {unidade['cidade']} - {unidade['uf']} ===")
        
        with conn.cursor() as cursor:
            # Conta os Resgates
            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN REABILITACAO = 'V' THEN 1 ELSE 0 END)
                FROM RESGATE_ENCALHE 
                WHERE UF = :uf AND CIDADE = :cidade
            """, {"uf": unidade["uf"], "cidade": unidade["cidade"]})
            res_resgates = cursor.fetchone()
            total_resgates = res_resgates[0] or 0
            reab_resgates = res_resgates[1] or 0

            # Conta as Pescas
            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN CLASSE = 'Monitorada' THEN 1 ELSE 0 END)
                FROM PESCA 
                WHERE UF = :uf AND CIDADE = :cidade
            """, {"uf": unidade["uf"], "cidade": unidade["cidade"]})
            res_pescas = cursor.fetchone()
            total_pescas = res_pescas[0] or 0
            pescas_monitoradas = res_pescas[1] or 0

            # Conta as Desovas (e faz um join rápido com Ninho para pegar estatísticas biológicas)
            cursor.execute("""
                SELECT COUNT(D.CODIGO_ANILHA), SUM(N.N_OVOS), SUM(N.N_FILHOTES)
                FROM DESOVA D
                JOIN NINHO N ON D.CODIGO_ESTACA = N.CODIGO_ESTACA
                WHERE D.UF = :uf AND D.CIDADE = :cidade
            """, {"uf": unidade["uf"], "cidade": unidade["cidade"]})
            res_desovas = cursor.fetchone()
            total_desovas = res_desovas[0] or 0
            total_ovos = res_desovas[1] or 0
            total_filhotes = res_desovas[2] or 0

        # Exibição do Dashboard no Terminal
        print("\n--- RESGATES E ENCALHES ---")
        print(f"Total de Ocorrências : {total_resgates}")
        print(f"Animais Reabilitados : {reab_resgates}")
        
        print("\n--- ATIVIDADE DE PESCA ---")
        print(f"Total de Ocorrências : {total_pescas}")
        print(f"Pescas Monitoradas   : {pescas_monitoradas}")
        
        print("\n--- MONITORAMENTO DE DESOVAS ---")
        print(f"Total de Ninhos      : {total_desovas}")
        print(f"Ovos Contabilizados  : {total_ovos}")
        print(f"Filhotes Nascidos    : {total_filhotes}")
        
        if total_ovos > 0:
            taxa = (total_filhotes / total_ovos) * 100
            print(f"Taxa de Eclosão Média: {taxa:.2f}%")

        print("\n=======================================================")
        print(f"VOLUME TOTAL DE EVENTOS NA ÁREA: {total_resgates + total_pescas + total_desovas}")
        print("=======================================================")

    except Exception as e:
        print("\n[Erro] Falha ao extrair estatísticas da área.")
        print(e)

# funções museu 
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
        print("1 - Registrar resgate/encalhe")
        print("2 - Registrar pesca")
        print("3 - Registrar desova")
        print("4 - Consultar histórico de uma tartaruga")
        print("5 - Consultar estatísticas da área")
        print("0 - Voltar")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            registrar_resgate_encalhe(conn, unidade)
        elif opcao == "2":
            registrar_pesca(conn, unidade)
        elif opcao == "3":
            registrar_desova(conn, unidade)
        elif opcao == "4":
            consultar_historico_tartaruga(conn)
        elif opcao == "5":
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
