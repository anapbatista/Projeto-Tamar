import oracledb

def conectar():

    senha = input("Senha Oracle: ")
    
    try:
        conn = oracledb.connect(
            user="a12688424",
            password=senha,
            host="orclgrad1.icmc.usp.br",
            port=1521,
            service_name="pdb_elaine.icmc.usp.br"
        )

        print("Conectado com sucesso!")
        return conn

    except oracledb.DatabaseError as e:
        print("Erro ao conectar:")
        print(e)
        return None