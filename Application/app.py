from database import conectar
from datetime import datetime

# UTILIDADES GERAIS
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

def obter_ou_cadastrar_pessoa(cursor, cpf):
    """Módulo reaproveitável para Lojas e Museus: Busca a pessoa pelo CPF ou aciona o cadastro."""
    cursor.execute("""
        SELECT NOME, PRIORIDADE_LEI
        FROM PESSOA
        WHERE CPF = :cpf
    """, {"cpf": cpf})

    resultado = cursor.fetchone()

    if resultado is not None:
        return resultado[0], resultado[1]  # Retorna: nome, prioridade

    print("\nCliente/Visitante não encontrado.")
    print("=== NOVO CADASTRO ===")
    nome = input("Nome: ").strip()

    while True:
        data_nasc_str = input("Data de nascimento (DD/MM/YYYY): ").strip()
        try:
            data_nasc_obj = datetime.strptime(data_nasc_str, "%d/%m/%Y")
            if data_nasc_obj > datetime.now():
                print("[Erro] A data de nascimento não pode ser no futuro.")
                continue
            break
        except ValueError:
            print("[Erro] Formato inválido. Use DD/MM/YYYY.")

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
    if opc == "2": prioridade = "Estudante"
    elif opc == "3": prioridade = "Idoso"
    elif opc == "4": prioridade = "Gestante"

    cursor.execute("""
        INSERT INTO PESSOA (CPF, NOME, DATA_NASCIM, FUNCAO, PRIORIDADE_LEI)
        VALUES (:cpf, :nome, TO_DATE(:data_nasc,'DD/MM/YYYY'), NULL, :prioridade)
    """, {
        "cpf": cpf,
        "nome": nome,
        "data_nasc": data_nasc_str,
        "prioridade": prioridade
    })

    print("\nCadastro realizado com sucesso.")
    return nome, prioridade


# FUNÇÕES LOJA
def registrar_pedido(conn, unidade):
    try:
        cpf = input("\nCPF do cliente: ").strip()
        if not cpf.isdigit():
            print("CPF deve conter apenas números.")
            return

        with conn.cursor() as cursor:
            # Substituído pelo módulo reutilizável
            nome, prioridade = obter_ou_cadastrar_pessoa(cursor, cpf)

            # Verifica se já existe relacionamento VENDE_PARA
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
                    INSERT INTO VENDE_PARA (CPF, UF, CIDADE)
                    VALUES (:cpf, :uf, :cidade)
                """, {
                    "cpf": cpf,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"]
                })

            while True:
                try:
                    valor = float(input("Valor do pedido: R$ ").replace(",", "."))
                    if valor <= 0:
                        print("O valor deve ser maior que zero.")
                        continue
                    break
                except ValueError:
                    print("Valor inválido.")

            cursor.execute("""
                INSERT INTO PEDIDO (CPF, UF, CIDADE, DATA_HORA, VALOR)
                VALUES (:cpf, :uf, :cidade, SYSDATE, :valor)
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
        print(f"Prioridade...: {prioridade if prioridade else 'Nenhuma'}")
        print(f"Loja.........: {unidade['uf']} - {unidade['cidade']}")
        print(f"Valor........: R$ {valor:.2f}")
        print(f"Data/Hora....: {momento.strftime('%d/%m/%Y %H:%M:%S')}")
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
                  AND EXTRACT(MONTH FROM DATA_HORA) = EXTRACT(MONTH FROM SYSDATE)
                  AND EXTRACT(YEAR FROM DATA_HORA) = EXTRACT(YEAR FROM SYSDATE)
            """, {
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            resultado = cursor.fetchone()
            qtd_pedidos, faturamento, ticket_medio, menor_pedido, maior_pedido = resultado

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
                  AND EXTRACT(MONTH FROM DATA_HORA) = EXTRACT(MONTH FROM SYSDATE)
                  AND EXTRACT(YEAR FROM DATA_HORA) = EXTRACT(YEAR FROM SYSDATE)
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
            print(f"{'CPF':<15} {'DATA':<20} {'VALOR':>10}")
            print("-" * 50)

            for cpf, data_hora, valor in pedidos:
                total += valor
                print(f"{cpf:<15} {data_hora:<20} R$ {valor:>7.2f}")

            print("-" * 50)
            print(f"Total de pedidos: {len(pedidos)}")
            print(f"Valor movimentado: R$ {total:.2f}")

    except Exception as e:
        print(f"\nErro ao consultar pedidos: {e}")


# FUNÇÕES AREA DE MONITORAMENTO & MODULARIZAÇÃO
def obter_data_hora_evento():
    """Captura a data e hora verificando e impedindo que seja no futuro."""
    while True:
        dt_str = input("\nData e Hora do evento (DD/MM/AAAA HH (00-23): ").strip()
        try:
            dt_obj = datetime.strptime(dt_str, "%d/%m/%Y %H")
            if dt_obj > datetime.now():
                print("[Erro] A data e hora do evento não podem estar no futuro.")
                continue
            return dt_obj.strftime("%d/%m/%Y %H:00:00")
        except ValueError:
            print("[Erro] Formato inválido. Digite no padrão DD/MM/AAAA HH (00-23) (Ex: 21/06/2026 14).")

def verificar_conflito_temporal(cursor, codigo_anilha, data_hora_str):
    cursor.execute("""
        SELECT CLASSIFICACAO 
        FROM CLASSIFICACOES 
        WHERE CODIGO_ANILHA = :codigo 
          AND DATA_HORA = TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS')
    """, {"codigo": codigo_anilha, "dt": data_hora_str})
    
    resultado = cursor.fetchone()
    if resultado is not None:
        print(f"\n[Erro de Unicidade] A tartaruga {codigo_anilha} já possui um evento de '{resultado[0]}' registrado nesta exata hora.")
        return True
    return False

def obter_pesquisador(cursor):
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
            
            # Nova Lógica: Selecionar a espécie do banco de dados em vez de digitar
            cursor.execute("SELECT NOME_CIENTIFICO FROM ESPECIE ORDER BY NOME_CIENTIFICO")
            especies = cursor.fetchall()
            
            if not especies:
                print("[Erro] Não há espécies cadastradas no sistema. Cadastre uma Espécie primeiro.")
                return None
                
            while True:
                print("\nEspécies catalogadas no sistema:")
                for i, (esp,) in enumerate(especies, start=1):
                    print(f"{i} - {esp}")
                try:
                    opc_esp = int(input("Escolha o número correspondente à espécie: "))
                    if 1 <= opc_esp <= len(especies):
                        nome_especie = especies[opc_esp - 1][0]
                        break
                    print("[Erro] Opção inválida.")
                except ValueError:
                    print("[Erro] Digite um número válido.")

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

            data_hora_str = obter_data_hora_evento()
            if verificar_conflito_temporal(cursor, codigo_anilha, data_hora_str):
                return

            motivo = input("\nMotivo do resgate/encalhe (Enter para nulo): ").strip()
            motivo = motivo if motivo != "" else None

            vivo = obter_input_vf("A tartaruga foi encontrada viva? (V/F ou Enter): ")
            reabilitacao = obter_input_vf("Será encaminhada para reabilitação? (V/F ou Enter): ")

            if vivo == "V" and reabilitacao != "V":
                print("\n[Nota do Sistema] Conforme protocolo do Projeto Tamar, tartarugas vivas resgatadas devem ir para reabilitação.")
                reabilitacao = "V"

            cursor.execute("""
                INSERT INTO CLASSIFICACOES (CODIGO_ANILHA, DATA_HORA, CLASSIFICACAO)
                VALUES (:codigo, TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS'), 'Resgate')
            """, {"codigo": codigo_anilha, "dt": data_hora_str})

            cursor.execute("""
                INSERT INTO RESGATE_ENCALHE (CODIGO_ANILHA, DATA_HORA, UF, CIDADE, CPF_PESQ, MOTIVO, VIVO, REABILITACAO)
                VALUES (:codigo, TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS'), :uf, :cidade, :cpf_pesq, :motivo, :vivo, :reabilitacao)
            """, {
                "codigo": codigo_anilha, "dt": data_hora_str, "uf": unidade["uf"], 
                "cidade": unidade["cidade"], "cpf_pesq": cpf_pesq, 
                "motivo": motivo, "vivo": vivo, "reabilitacao": reabilitacao
            })

        conn.commit()
        
        print("\n====================================")
        print("         PROJETO TAMAR")
        print("====================================")
        print("Resgate/Encalhe registrado com sucesso")
        print("------------------------------------")
        print(f"Anilha Tartaruga: {codigo_anilha}")
        print(f"Pesquisador CPF.: {cpf_pesq}")
        print(f"Data/Hora Evento: {data_hora_str}")
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

            data_hora_str = obter_data_hora_evento()
            if verificar_conflito_temporal(cursor, codigo_anilha, data_hora_str):
                return

            # Nova Lógica: Selecionar o tipo de classe por menu
            while True:
                print("\nClasse da Pesca:")
                print("1 - Monitorada")
                print("2 - Não Monitorada")
                print("0 - Nulo (Pular)")
                opc_classe = input("Escolha uma opção: ").strip()
                
                if opc_classe == "1":
                    classe = "Monitorada"
                    break
                elif opc_classe == "2":
                    classe = "Não Monitorada"
                    break
                elif opc_classe == "0":
                    classe = None
                    break
                print("[Erro] Opção inválida.")

            reabilitacao = obter_input_vf("Foi encaminhada para reabilitação? (V/F ou Enter): ")

            if classe == "Não Monitorada" and reabilitacao != "V":
                print("\n[Nota do Sistema] Capturas acidentais locais exigem reabilitação preventiva.")
                reabilitacao = "V"

            cursor.execute("""
                INSERT INTO CLASSIFICACOES (CODIGO_ANILHA, DATA_HORA, CLASSIFICACAO)
                VALUES (:codigo, TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS'), 'Pesca')
            """, {"codigo": codigo_anilha, "dt": data_hora_str})

            cursor.execute("""
                INSERT INTO PESCA (CODIGO_ANILHA, DATA_HORA, UF, CIDADE, CPF_PESQ, CLASSE, REABILITACAO)
                VALUES (:codigo, TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS'), :uf, :cidade, :cpf_pesq, :classe, :reabilitacao)
            """, {
                "codigo": codigo_anilha, "dt": data_hora_str, "uf": unidade["uf"], 
                "cidade": unidade["cidade"], "cpf_pesq": cpf_pesq, 
                "classe": classe, "reabilitacao": reabilitacao
            })

        conn.commit()

        print("\n====================================")
        print("         PROJETO TAMAR")
        print("====================================")
        print("Evento de Pesca registrado com sucesso")
        print("------------------------------------")
        print(f"Anilha Tartaruga: {codigo_anilha}")
        print(f"Pesquisador CPF.: {cpf_pesq}")
        print(f"Data/Hora Evento: {data_hora_str}")
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

            data_hora_str = obter_data_hora_evento()
            if verificar_conflito_temporal(cursor, codigo_anilha, data_hora_str):
                return

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
                VALUES (:codigo, TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS'), 'Desova')
            """, {"codigo": codigo_anilha, "dt": data_hora_str})

            cursor.execute("""
                INSERT INTO DESOVA (CODIGO_ANILHA, DATA_HORA, UF, CIDADE, CPF_PESQ, CODIGO_ESTACA)
                VALUES (:codigo, TO_DATE(:dt, 'DD/MM/YYYY HH24:MI:SS'), :uf, :cidade, :cpf_pesq, :codigo_estaca)
            """, {
                "codigo": codigo_anilha, "dt": data_hora_str, "uf": unidade["uf"], 
                "cidade": unidade["cidade"], "cpf_pesq": cpf_pesq, "codigo_estaca": codigo_estaca
            })

        conn.commit()

        print("\n====================================")
        print("         PROJETO TAMAR")
        print("====================================")
        print("Evento de Desova registrado com sucesso")
        print("------------------------------------")
        print(f"Anilha Tartaruga: {codigo_anilha}")
        print(f"Código Estaca...: {codigo_estaca}")
        print(f"Data/Hora Evento: {data_hora_str}")
        print("====================================")

    except Exception as e:
        conn.rollback()
        print("\nErro ao registrar o evento de desova.")
        print(e)

def consultar_historico_tartaruga(conn):
    try:
        print("\n=== CONSULTAR HISTÓRICO DE TARTARUGA ===")
        codigo_anilha = input("Digite o Código da Anilha: ").strip().upper()
        
        if not codigo_anilha:
            print("[Erro] O código da anilha não pode ser vazio.")
            return

        with conn.cursor() as cursor:
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
    try:
        print(f"\n=== ESTATÍSTICAS DA BASE: {unidade['cidade']} - {unidade['uf']} ===")
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN REABILITACAO = 'V' THEN 1 ELSE 0 END)
                FROM RESGATE_ENCALHE 
                WHERE UF = :uf AND CIDADE = :cidade
            """, {"uf": unidade["uf"], "cidade": unidade["cidade"]})
            res_resgates = cursor.fetchone()
            total_resgates = res_resgates[0] or 0
            reab_resgates = res_resgates[1] or 0

            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN CLASSE = 'Monitorada' THEN 1 ELSE 0 END)
                FROM PESCA 
                WHERE UF = :uf AND CIDADE = :cidade
            """, {"uf": unidade["uf"], "cidade": unidade["cidade"]})
            res_pescas = cursor.fetchone()
            total_pescas = res_pescas[0] or 0
            pescas_monitoradas = res_pescas[1] or 0

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

# FUNÇÕES MUSEU
def vender_ingresso(conn, unidade):
    try:
        cpf = input("\nCPF do visitante: ").strip()
        if not cpf.isdigit():
            print("CPF deve conter apenas números.")
            return

        with conn.cursor() as cursor:
            nome, prioridade = obter_ou_cadastrar_pessoa(cursor, cpf)

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
                    INSERT INTO VISITA (CPF, UF, CIDADE)
                    VALUES (:cpf, :uf, :cidade)
                """, {
                    "cpf": cpf,
                    "uf": unidade["uf"],
                    "cidade": unidade["cidade"]
                })

            if prioridade == 'Idoso':
                categoria = 'Gratuidade'
                valor = 0.00
            elif prioridade is not None:
                categoria = 'Meia'
                valor = 20.00
            else:
                categoria = 'Inteira'
                valor = 40.00

            # Cadastro do ingresso
            cursor.execute("""
                INSERT INTO INGRESSO (CPF, UF, CIDADE, DATA_HORA, VALOR, CATEGORIA)
                VALUES (:cpf, :uf, :cidade, SYSDATE, :valor, :categoria)
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
        print(f"Prioridade...: {prioridade if prioridade else 'Nenhuma'}")
        print(f"Museu........: {unidade['uf']} - {unidade['cidade']}")
        print(f"Valor........: R$ {valor:.2f}")
        print(f"Data/Hora....: {momento.strftime('%d/%m/%Y %H:%M:%S')}")
        print("====================================")

    except Exception as e:
        conn.rollback()
        print("\nErro ao registrar pedido.")
        print(e)

def consultar_faturamento_museu(conn, unidade):
    try:
        with conn.cursor() as cursor:
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
                  AND EXTRACT(MONTH FROM DATA_HORA) = EXTRACT(MONTH FROM SYSDATE)
                  AND EXTRACT(YEAR FROM DATA_HORA) = EXTRACT(YEAR FROM SYSDATE)
            """, {
                "uf": unidade["uf"],
                "cidade": unidade["cidade"]
            })

            resultado = cursor.fetchone()
            qtd_ingressos = resultado[0] 
            faturamento = resultado[1] 
            qtd_gratuidade = resultado[2] 
            qtd_meia = resultado[3] 
            qtd_inteira = resultado[4] 

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

def consultar_visitantes_dia(conn, unidade):
    try:
        with conn.cursor() as cursor:
            # Lógica de bloqueio para datas não passarem do presente momento
            while True:
                data = input("Data (DD/MM/YYYY): ").strip()
                try:
                    dt_obj = datetime.strptime(data, "%d/%m/%Y")
                    if dt_obj > datetime.now():
                        print("[Erro] Não é possível consultar datas no futuro.")
                        continue
                    break
                except ValueError:
                    print("[Erro] Formato inválido. Use DD/MM/YYYY.")

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
            print(f"{'CPF':<15} {'DATA':<20} {'VALOR':>11}")
            print("-" * 50)

            for cpf, data_hora, categoria, valor in ingressos:
                total += valor
                print(f"{cpf:<15} {data_hora:<20} {categoria:>11}")

            print("-" * 50)
            print(f"Total de ingressos: {len(ingressos)}")
            print(f"Valor movimentado: R$ {total:.2f}")

    except Exception as e:
        print(f"\nErro ao consultar ingressos: {e}")


# MENUS
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


# CONSULTA 5 - RESUMO OPERACIONAL POR BASE: DASHBOARD
def exibir_dashboard_estados(conn):
    try:
        print("\n" + "=" * 75)
        print(" DASHBOARD EXECUTIVO: RESUMO DAS BASES POR ESTADO ".center(75))
        print("=" * 75)

        sql = """
            WITH 
            -- 1. ESTRUTURA FÍSICA
            CTE_Lojas AS (SELECT UF, COUNT(*) AS qtd_lojas FROM Loja GROUP BY UF),
            CTE_Museus AS (SELECT UF, COUNT(*) AS qtd_museus FROM Museu GROUP BY UF),
            CTE_Areas AS (SELECT UF, COUNT(*) AS qtd_areas FROM Area_de_Monitoramento GROUP BY UF),

            -- 2. FINANCEIRO E PÚBLICO
            CTE_Pedidos AS (
                SELECT UF, SUM(valor) AS total_pedidos, COUNT(DISTINCT CPF) AS qtd_clientes 
                FROM Pedido GROUP BY UF
            ),
            CTE_Ingressos AS (
                SELECT UF, SUM(valor) AS total_ingressos, COUNT(DISTINCT CPF) AS qtd_visitantes 
                FROM Ingresso GROUP BY UF
            ),

            -- 3. RECURSOS HUMANOS E CUSTOS LOCAIS (Abordagem UNION + CASE WHEN)
            CTE_Pesquisadores_UF AS (
                SELECT CPF_Pesq AS CPF, UF FROM Resgate_Encalhe UNION
                SELECT CPF_Pesq AS CPF, UF FROM Pesca UNION
                SELECT CPF_Pesq AS CPF, UF FROM Desova
            ),
            CTE_Equipe_Itens AS (
                SELECT CPF, UF, 'FUNCIONARIO' AS tipo, NVL(remuneracao, 0) AS custo FROM Funcionario
                UNION ALL
                SELECT CPF, UF, 'ARTESAO' AS tipo, NVL(subsidio, 0) AS custo FROM Artesao
                UNION ALL
                SELECT pu.CPF, pu.UF, 'PESQUISADOR' AS tipo, NVL(p.remuneracao, 0) AS custo 
                FROM CTE_Pesquisadores_UF pu 
                JOIN Pesquisador p ON p.CPF = pu.CPF
            ),
            CTE_Equipe AS (
                SELECT 
                    UF,
                    COUNT(DISTINCT CPF) AS total_colaboradores,
                    COUNT(DISTINCT CASE WHEN tipo = 'FUNCIONARIO' THEN CPF END) AS qtd_funcionarios,
                    COUNT(DISTINCT CASE WHEN tipo = 'PESQUISADOR' THEN CPF END) AS qtd_pesquisadores,
                    COUNT(DISTINCT CASE WHEN tipo = 'ARTESAO' THEN CPF END) AS qtd_artesaos,
                    SUM(custo) AS custo_equipe
                FROM CTE_Equipe_Itens
                GROUP BY UF
            ),

            -- 4. MONITORAMENTO E CONSERVAÇÃO
            CTE_Resgates AS (
                SELECT UF, COUNT(*) AS total_resgates, 
                       SUM(CASE WHEN reabilitacao = 'V' THEN 1 ELSE 0 END) AS qtd_reab_resgate
                FROM Resgate_Encalhe GROUP BY UF
            ),
            CTE_Pescas AS (
                SELECT UF, COUNT(*) AS total_pescas, 
                       SUM(CASE WHEN classe = 'Monitorada' THEN 1 ELSE 0 END) AS pescas_monitoradas,
                       SUM(CASE WHEN reabilitacao = 'V' THEN 1 ELSE 0 END) AS qtd_reab_pesca
                FROM Pesca GROUP BY UF
            ),
            CTE_Desovas AS (
                SELECT d.UF, COUNT(d.codigo_anilha) AS total_desovas, 
                       SUM(n.n_ovos) AS total_ovos, SUM(n.n_filhotes) AS total_filhotes
                FROM Desova d
                JOIN Ninho n ON d.codigo_estaca = n.codigo_estaca
                GROUP BY d.UF
            ),
            CTE_Tartarugas AS (
                SELECT UF, COUNT(DISTINCT codigo_anilha) AS qtd_tartarugas
                FROM (
                    SELECT UF, codigo_anilha FROM Resgate_Encalhe UNION
                    SELECT UF, codigo_anilha FROM Pesca UNION
                    SELECT UF, codigo_anilha FROM Desova
                ) GROUP BY UF
            )

            -- SELEÇÃO FINAL: CONSOLIDANDO TODAS AS CTEs POR ESTADO
            SELECT 
                b.UF AS "Estado",

                -- Estrutura Física
                NVL(l.qtd_lojas, 0) AS "Lojas",
                NVL(m.qtd_museus, 0) AS "Museus",
                NVL(a.qtd_areas, 0) AS "Áreas de Monitoramento",

                -- Financeiro e Público
                NVL(p.total_pedidos, 0) + NVL(i.total_ingressos, 0) AS "Arrecadação Total (R$)",
                NVL(p.qtd_clientes, 0) AS "Clientes",
                NVL(i.qtd_visitantes, 0) AS "Visitantes",

                -- Equipe Base
                NVL(eq.qtd_funcionarios, 0) AS "Funcionários",
                NVL(eq.qtd_pesquisadores, 0) AS "Pesquisadores",
                NVL(eq.qtd_artesaos, 0) AS "Artesãos",
                NVL(eq.custo_equipe, 0) AS "Custo Equipe Local (R$)",

                -- Eventos Gerais
                NVL(r.total_resgates, 0) + NVL(pe.total_pescas, 0) + NVL(d.total_desovas, 0) AS "Total de Eventos",
                NVL(t.qtd_tartarugas, 0) AS "Tartarugas Monitoradas",

                -- Detalhamento de Resgates e Reabilitação
                NVL(r.total_resgates, 0) AS "Total Resgates",
                ROUND(NVL(r.total_resgates, 0) / NULLIF(a.qtd_areas, 0), 2) AS "Média Resgates/Área",
                ROUND(
                    (NVL(r.qtd_reab_resgate, 0) + NVL(pe.qtd_reab_pesca, 0)) * 100.0 / 
                    NULLIF(NVL(r.total_resgates, 0) + NVL(pe.total_pescas, 0), 0), 2
                ) AS "Taxa de Reabilitação (%)",

                -- Detalhamento de Pescas
                NVL(pe.total_pescas, 0) AS "Total Pescas",
                NVL(pe.pescas_monitoradas, 0) AS "Pescas Monitoradas",

                -- Detalhamento de Desovas
                NVL(d.total_desovas, 0) AS "Total Desovas",
                ROUND(NVL(d.total_filhotes, 0) * 100.0 / NULLIF(d.total_ovos, 0), 2) AS "Taxa de Eclosão (%)"

            FROM (SELECT DISTINCT UF FROM Base) b
            LEFT JOIN CTE_Lojas l ON b.UF = l.UF
            LEFT JOIN CTE_Museus m ON b.UF = m.UF
            LEFT JOIN CTE_Areas a ON b.UF = a.UF
            LEFT JOIN CTE_Pedidos p ON b.UF = p.UF
            LEFT JOIN CTE_Ingressos i ON b.UF = i.UF
            LEFT JOIN CTE_Equipe eq ON b.UF = eq.UF 
            LEFT JOIN CTE_Resgates r ON b.UF = r.UF
            LEFT JOIN CTE_Pescas pe ON b.UF = pe.UF
            LEFT JOIN CTE_Desovas d ON b.UF = d.UF
            LEFT JOIN CTE_Tartarugas t ON b.UF = t.UF
            ORDER BY "Arrecadação Total (R$)" DESC, b.UF
        """

        with conn.cursor() as cursor:
            cursor.execute(sql)
            resultados = cursor.fetchall()

        if not resultados:
            print("\n[Aviso] Nenhum dado encontrado para gerar o dashboard.")
            return

        for row in resultados:
            (uf, lojas, museus, areas, arrecadacao, clientes, visitantes,
             funcionarios, pesquisadores, artesaos, custo_equipe,
             total_eventos, tartarugas, total_resgates, media_resgates,
             taxa_reab, total_pescas, pescas_monit, total_desovas, taxa_eclosao) = row

            media_resgates = media_resgates if media_resgates is not None else 0.0
            taxa_reab = taxa_reab if taxa_reab is not None else 0.0
            taxa_eclosao = taxa_eclosao if taxa_eclosao is not None else 0.0

            print(f"\n[{uf}] RELATÓRIO ESTADUAL ".ljust(75, "-"))
            print(f" ESTRUTURA:   {lojas} Loja(s) | {museus} Museu(s) | {areas} Área(s) de Monitoramento")
            print(f" FINANCEIRO:  Arrecadação Total: R$ {arrecadacao:,.2f}")
            print(f"                 Público Atendido: {clientes} Cliente(s) | {visitantes} Visitante(s)")
            print(f" EQUIPE:      Custo Local: R$ {custo_equipe:,.2f}")
            print(f"                 Membros: {funcionarios} Funcionário(s) | {pesquisadores} Pesquisador(es) | {artesaos} Artesão(s)")
            print(f" AMBIENTAL:   Total de Eventos: {total_eventos} | Tartarugas Monitoradas: {tartarugas}")
            print(f"                 - Resgates: {total_resgates} (Média por Área: {media_resgates:.1f})")
            print(f"                 - Pescas:   {total_pescas} ({pescas_monit} monitoradas)")
            print(f"                 - Desovas:  {total_desovas} (Taxa de Eclosão: {taxa_eclosao:.1f}%)")
            print(f"                 >> Taxa Geral de Reabilitação (Pesca/Resgate): {taxa_reab:.1f}%")
        
        print("\n" + "=" * 75)

    except Exception as e:
        print("\n[Erro] Falha ao executar a consulta do dashboard.")
        print(e)


# MAIN
def menu_principal():
    print("\n====================================")
    print(" SISTEMA PROJETO TAMAR")
    print("====================================")
    print("1 - Área de Monitoramento")
    print("2 - Museu")
    print("3 - Loja")
    print("4 - Cadastrar nova unidade")
    print("5 - Resumo operacional por base")
    print("0 - Sair")

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
                unidade = selecionar_unidade(conn, "AREA_DE_MONITORAMENTO", "Área de Monitoramento")
                if unidade:
                    menu_monitoramento(conn, unidade)

            elif opcao == "2":
                unidade = selecionar_unidade(conn, "MUSEU", "Museu")
                if unidade:
                    menu_museu(conn, unidade)

            elif opcao == "3":
                unidade = selecionar_unidade(conn, "LOJA", "Loja")
                if unidade:
                    menu_loja(conn, unidade)

            elif opcao == "4":
                print("\nAcesso negado.")
                print("Somente usuários com credencial de gerente podem cadastrar novas unidades.")

            elif opcao == "5":
                exibir_dashboard_estados(conn)

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
