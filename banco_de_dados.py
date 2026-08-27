import sqlite3


def conectar():

    conexao = sqlite3.connect("database.db")

    conexao.row_factory = sqlite3.Row

    return conexao


def criar_banco():

    conexao = conectar()

    cursor = conexao.cursor()

    # ==========================================
    # TABELA DE USUÁRIOS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==========================================
    # TABELA DE VERIFICAÇÃO DE E-MAIL
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verificacoes_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            codigo TEXT NOT NULL,
            expiracao TIMESTAMP NOT NULL,
            tentativas INTEGER DEFAULT 0,
            verificado INTEGER DEFAULT 0
        )
    """)

    # ==========================================
    # TABELA DE CHATS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id)
            REFERENCES usuarios(id)
        )
    """)

    # ==========================================
    # TABELA DE MENSAGENS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (chat_id)
            REFERENCES chats(id)
        )
    """)

    conexao.commit()

    conexao.close()