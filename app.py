import os

import secrets

from datetime import datetime, timedelta

import requests

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash
)

from dotenv import load_dotenv

from flask_mail import Mail, Message

from authlib.integrations.flask_client import OAuth

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from email_validator import (
    validate_email,
    EmailNotValidError
)

from professor import responder_pergunta

from banco_de_dados import conectar

# ==========================================
# CARREGAR .ENV
# ==========================================

load_dotenv()
# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "chave-temporaria-estuda-ia"
)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_REMETENTE")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_SENHA_APP")
mail = Mail(app)

# ==========================================
# GOOGLE OAUTH

# ==========================================
# FLASK
# ==========================================

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "chave-temporaria-estuda-ia"
)

# ==========================================
# GOOGLE OAUTH
# ==========================================

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid profile email"
    }
)


# ==========================================
# IDENTIFICAR ASSUNTO
# ==========================================

def identificar_assunto(pergunta):

    texto = pergunta.lower()

    assuntos = {

        "bhaskara": [
            "bhaskara",
            "báskara",
            "basckara",
            "delta"
        ],

        "porcentagem": [
            "porcentagem",
            "percentual",
            "%"
        ],

        "frações": [
            "fração",
            "frações",
            "fracao",
            "fracoes"
        ],

        "equação do 1º grau": [
            "equação do primeiro grau",
            "equacao do primeiro grau",
            "equação de primeiro grau",
            "equacao de primeiro grau",
            "1º grau"
        ],

        "equação do 2º grau": [
            "equação do segundo grau",
            "equacao do segundo grau",
            "equação de segundo grau",
            "equacao de segundo grau",
            "2º grau"
        ],

        "regra de três": [
            "regra de três",
            "regra de tres"
        ],

        "razão e proporção": [
            "razão",
            "razao",
            "proporção",
            "proporcao"
        ],

        "potenciação": [
            "potenciação",
            "potenciacao",
            "potência",
            "potencia"
        ],

        "radiciação": [
            "radiciação",
            "radiciacao",
            "raiz quadrada",
            "raiz"
        ],

        "teorema de pitágoras": [
            "pitágoras",
            "pitagoras",
            "teorema de pitágoras",
            "teorema de pitagoras"
        ],

        "probabilidade": [
            "probabilidade",
            "probabilidades"
        ],

        "estatística": [
            "estatística",
            "estatistica",
            "média",
            "media",
            "mediana",
            "moda"
        ],

        "fotossíntese": [
            "fotossíntese",
            "fotossintese"
        ],

        "história": [
            "história",
            "historia"
        ],

        "geografia": [
            "geografia"
        ],

        "ciências": [
            "ciências",
            "ciencias"
        ],

        "português": [
            "português",
            "portugues",
            "gramática",
            "gramatica"
        ]
    }

    for assunto, palavras in assuntos.items():

        for palavra in palavras:

            if palavra in texto:
                return assunto.title()

    titulo = pergunta.strip()

    if len(titulo) > 40:
        titulo = titulo[:40].strip() + "..."

    return titulo


# ==========================================
# CRIAR TÍTULO ÚNICO
# ==========================================

def criar_titulo_unico(usuario_id, assunto):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT titulo
        FROM chats
        WHERE usuario_id = ?
        """,
        (usuario_id,)
    )

    chats = cursor.fetchall()

    conexao.close()

    titulos = []

    for chat in chats:

        titulos.append(
            chat["titulo"].lower()
        )

    if assunto.lower() not in titulos:
        return assunto

    numero = 2

    while True:

        novo_titulo = f"{assunto} {numero}"

        if novo_titulo.lower() not in titulos:
            return novo_titulo

        numero += 1


# ==========================================
# PEGAR OU CRIAR CHAT
# ==========================================

def obter_chat_usuario(usuario_id):

    conexao = conectar()
    cursor = conexao.cursor()

    chat_id = session.get("chat_id")

    chat = None

    if chat_id:

        cursor.execute(
            """
            SELECT *
            FROM chats
            WHERE id = ?
            AND usuario_id = ?
            """,
            (
                chat_id,
                usuario_id
            )
        )

        chat = cursor.fetchone()

    if chat is None:

        cursor.execute(
            """
            SELECT *
            FROM chats
            WHERE usuario_id = ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (usuario_id,)
        )

        chat = cursor.fetchone()

    if chat is None:

        cursor.execute(
            """
            INSERT INTO chats
            (usuario_id, titulo)
            VALUES (?, ?)
            """,
            (
                usuario_id,
                "Nova conversa"
            )
        )

        conexao.commit()

        chat_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT *
            FROM chats
            WHERE id = ?
            """,
            (chat_id,)
        )

        chat = cursor.fetchone()

    conexao.close()

    session["chat_id"] = chat["id"]

    return chat


# ==========================================
# CARREGAR HISTÓRICO
# ==========================================

def carregar_historico(chat_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT pergunta, resposta
        FROM mensagens
        WHERE chat_id = ?
        ORDER BY id ASC
        """,
        (chat_id,)
    )

    mensagens = cursor.fetchall()

    conexao.close()

    historico = []

    for mensagem in mensagens:

        historico.append(
            {
                "pergunta": mensagem["pergunta"],
                "resposta": mensagem["resposta"]
            }
        )

    return historico


# ==========================================
# CARREGAR TODOS OS CHATS
# ==========================================

def carregar_chats(usuario_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, titulo
        FROM chats
        WHERE usuario_id = ?
        ORDER BY id DESC
        """,
        (usuario_id,)
    )

    chats = cursor.fetchall()

    conexao.close()

    return chats


# ==========================================
# ENVIAR CÓDIGO POR E-MAIL
# ==========================================

def enviar_codigo_email(email, codigo):

    try:

        import os
    

        api_key = os.getenv("SENDLIB_API_KEY")

        if not api_key:
            print(
                "ERRO: SENDLIB_API_KEY não encontrada no .env"
            )
            return False

        resposta = requests.post(
            "https://sendlib.samueltuoyo.com/api/send",

            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },

            json={
                "from": "estudaiagmail@gmail.com",
                "to": email,
                "subject": "Código de verificação - Estuda IA",
                "html": f"""
                    <div style="font-family: Arial, sans-serif;">

                        <h2>Estuda IA</h2>

                        <p>
                            Seu código de verificação é:
                        </p>

                        <h1 style="letter-spacing: 8px;">
                            {codigo}
                        </h1>

                        <p>
                            Este código é válido por 10 minutos.
                        </p>

                        <p>
                            Se você não solicitou este código,
                            ignore este e-mail.
                        </p>

                    </div>
                """
            },

            timeout=20
        )

        if 200 <= resposta.status_code < 300:

            print(
                "E-MAIL ENVIADO:",
                email
            )

            return True

        print(
            "ERRO SENDLIB:",
            resposta.status_code,
            resposta.text
        )

        return False

    except Exception as erro:

        print(
            "ERRO AO ENVIAR CÓDIGO:",
            erro
        )

        return False

# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    usuario_id = session["usuario_id"]

    chat = obter_chat_usuario(
        usuario_id
    )

    historico = carregar_historico(
        chat["id"]
    )

    chats = carregar_chats(
        usuario_id
    )

    return render_template(
        "index.html",
        historico=historico,
        chats=chats,
        chat_atual=chat
    )


# ==========================================
# ABRIR CHAT
# ==========================================

@app.route("/chat/<int:chat_id>")
def abrir_chat(chat_id):

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    usuario_id = session["usuario_id"]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT *
        FROM chats
        WHERE id = ?
        AND usuario_id = ?
        """,
        (
            chat_id,
            usuario_id
        )
    )

    chat = cursor.fetchone()

    conexao.close()

    if chat is None:

        return redirect(
            url_for("inicio")
        )

    session["chat_id"] = chat_id

    return redirect(
        url_for("inicio")
    )


# ==========================================
# PERGUNTAR PARA A IA
# ==========================================

@app.route("/perguntar", methods=["POST"])
def perguntar():

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    pergunta = request.form.get(
        "pergunta",
        ""
    ).strip()

    if not pergunta:

        return redirect(
            url_for("inicio")
        )

    usuario_id = session["usuario_id"]

    chat = obter_chat_usuario(
        usuario_id
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS quantidade
        FROM mensagens
        WHERE chat_id = ?
        """,
        (chat["id"],)
    )

    quantidade = cursor.fetchone()["quantidade"]

    if quantidade == 0:

        assunto = identificar_assunto(
            pergunta
        )

        titulo = criar_titulo_unico(
            usuario_id,
            assunto
        )

        cursor.execute(
            """
            UPDATE chats
            SET titulo = ?
            WHERE id = ?
            AND usuario_id = ?
            """,
            (
                titulo,
                chat["id"],
                usuario_id
            )
        )

        conexao.commit()

    conexao.close()

    # ==========================================
    # CARREGAR MEMÓRIA DA CONVERSA
    # ==========================================

    historico = carregar_historico(
        chat["id"]
    )

    # ==========================================
    # ENVIAR PERGUNTA + HISTÓRICO PARA O PROFESSOR
    # ==========================================

    resposta = responder_pergunta(
        pergunta,
        session,
        historico
    )

    # ==========================================
    # SALVAR NOVA MENSAGEM
    # ==========================================

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO mensagens
        (chat_id, pergunta, resposta)
        VALUES (?, ?, ?)
        """,
        (
            chat["id"],
            pergunta,
            resposta
        )
    )

    conexao.commit()
    conexao.close()

    return redirect(
        url_for("inicio")
    )


# ==========================================
# NOVA CONVERSA
# ==========================================

@app.route("/novo_chat")
def novo_chat():

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    usuario_id = session["usuario_id"]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO chats
        (usuario_id, titulo)
        VALUES (?, ?)
        """,
        (
            usuario_id,
            "Nova conversa"
        )
    )

    conexao.commit()

    novo_chat_id = cursor.lastrowid

    conexao.close()

    session["chat_id"] = novo_chat_id

    return redirect(
        url_for("inicio")
    )

# ==========================================
# ENVIAR CÓDIGO DE VERIFICAÇÃO POR E-MAIL
# ==========================================

def enviar_codigo_email(email, codigo):

    try:

        mensagem = Message(
            subject="Código de verificação - Estuda IA",
            sender=os.getenv("EMAIL_REMETENTE"),
            recipients=[email]
        )

        mensagem.body = (
            "Olá!\n\n"
            "Seu código de verificação do Estuda IA é:\n\n"
            f"{codigo}\n\n"
            "Esse código é válido por 10 minutos.\n\n"
            "Se você não solicitou esse cadastro, "
            "ignore este e-mail."
        )

        mail.send(mensagem)

        return True

    except Exception as erro:

        print(
            "ERRO AO ENVIAR E-MAIL:",
            erro
        )

        return False
# ==========================================
# CADASTRO
# ==========================================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "GET":

        return render_template(
            "cadastro.html"
        )

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    senha = request.form.get(
        "senha",
        ""
    )

    confirmar_senha = request.form.get(
        "confirmar_senha",
        ""
    )

    if not nome or not email or not senha:

        return "Preencha todos os campos."

    if senha != confirmar_senha:

        return "As senhas não são iguais."

    # ==========================================
    # VALIDAR E-MAIL
    # ==========================================

    try:

        email_validado = validate_email(
            email
        )

        email = email_validado.normalized

    except EmailNotValidError:

        return "Digite um e-mail válido."

    # ==========================================
    # VERIFICAR SE JÁ EXISTE
    # ==========================================

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    )

    usuario_existente = cursor.fetchone()

    conexao.close()

    if usuario_existente is not None:

        return "Este e-mail já está cadastrado."

    # ==========================================
    # GERAR CÓDIGO
    # ==========================================

    codigo = str(
        secrets.randbelow(900000) + 100000
    )

    expiracao = (
        datetime.now() + timedelta(minutes=10)
    ).isoformat()

    senha_hash = generate_password_hash(
        senha
    )

    # ==========================================
    # SALVAR DADOS TEMPORÁRIOS NA SESSÃO
    # ==========================================

    session["cadastro_pendente"] = {
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash
    }

    # ==========================================
    # SALVAR CÓDIGO NO BANCO
    # ==========================================

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM verificacoes_email
        WHERE email = ?
        """,
        (email,)
    )

    cursor.execute(
        """
        INSERT INTO verificacoes_email
        (email, codigo, expiracao, tentativas, verificado)
        VALUES (?, ?, ?, 0, 0)
        """,
        (
            email,
            codigo,
            expiracao
        )
    )

    conexao.commit()
    conexao.close()

    # ==========================================
    # ENVIAR E-MAIL
    # ==========================================

    enviado = enviar_codigo_email(
        email,
        codigo
    )

    if not enviado:

        session.pop(
            "cadastro_pendente",
            None
        )

        return (
            "Não foi possível enviar o "
            "código de verificação."
        )

    return redirect(
        url_for("verificar_email")
    )


# ==========================================
# VERIFICAR E-MAIL
# ==========================================

@app.route(
    "/verificar-email",
    methods=["GET", "POST"]
)
def verificar_email():

    cadastro_pendente = session.get(
        "cadastro_pendente"
    )

    if not cadastro_pendente:

        return redirect(
            url_for("cadastro")
        )

    email = cadastro_pendente["email"]

    if request.method == "GET":

        return render_template(
            "verificar_email.html",
            email=email
        )

    codigo_digitado = request.form.get(
        "codigo",
        ""
    ).strip()

    if not codigo_digitado:

        return "Digite o código recebido por e-mail."

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT *
        FROM verificacoes_email
        WHERE email = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (email,)
    )

    verificacao = cursor.fetchone()

    if verificacao is None:

        conexao.close()

        return "Código não encontrado. Faça o cadastro novamente."

    # ==========================================
    # VERIFICAR EXPIRAÇÃO
    # ==========================================

    try:

        expiracao = datetime.fromisoformat(
            verificacao["expiracao"]
        )

    except ValueError:

        conexao.close()

        return "Código inválido. Faça o cadastro novamente."

    if datetime.now() > expiracao:

        cursor.execute(
            """
            DELETE FROM verificacoes_email
            WHERE email = ?
            """,
            (email,)
        )

        conexao.commit()
        conexao.close()

        session.pop(
            "cadastro_pendente",
            None
        )

        return "O código expirou. Faça o cadastro novamente."

    # ==========================================
    # VERIFICAR CÓDIGO
    # ==========================================

    if codigo_digitado != verificacao["codigo"]:

        novas_tentativas = (
            verificacao["tentativas"] + 1
        )

        cursor.execute(
            """
            UPDATE verificacoes_email
            SET tentativas = ?
            WHERE id = ?
            """,
            (
                novas_tentativas,
                verificacao["id"]
            )
        )

        conexao.commit()
        conexao.close()

        if novas_tentativas >= 5:

            session.pop(
                "cadastro_pendente",
                None
            )

            return (
                "Número máximo de tentativas "
                "atingido. Faça o cadastro novamente."
            )

        return (
            f"Código incorreto. "
            f"Tentativas restantes: "
            f"{5 - novas_tentativas}"
        )

    # ==========================================
    # CRIAR CONTA
    # ==========================================

    dados = session.get(
        "cadastro_pendente"
    )

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    )

    usuario_existente = cursor.fetchone()

    if usuario_existente is not None:

        conexao.close()

        session.pop(
            "cadastro_pendente",
            None
        )

        return "Este e-mail já está cadastrado."

    cursor.execute(
        """
        INSERT INTO usuarios
        (nome, email, senha_hash)
        VALUES (?, ?, ?)
        """,
        (
            dados["nome"],
            dados["email"],
            dados["senha_hash"]
        )
    )

    usuario_id = cursor.lastrowid

    cursor.execute(
        """
        UPDATE verificacoes_email
        SET verificado = 1
        WHERE id = ?
        """,
        (verificacao["id"],)
    )

    conexao.commit()
    conexao.close()

    # ==========================================
    # LOGIN AUTOMÁTICO
    # ==========================================

    session.pop(
        "cadastro_pendente",
        None
    )

    session["usuario_id"] = usuario_id
    session["usuario_nome"] = dados["nome"]
    session["usuario_email"] = dados["email"]

    session.pop(
        "chat_id",
        None
    )

    obter_chat_usuario(
        usuario_id
    )

    return redirect(
        url_for("inicio")
    )


# ==========================================
# LOGIN NORMAL
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    senha = request.form.get(
        "senha",
        ""
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT *
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    )

    usuario = cursor.fetchone()

    conexao.close()

    if usuario is None:

        return "E-mail ou senha incorretos."

    if not check_password_hash(
        usuario["senha_hash"],
        senha
    ):

        return "E-mail ou senha incorretos."

    session["usuario_id"] = usuario["id"]

    session["usuario_nome"] = usuario["nome"]

    session["usuario_email"] = usuario["email"]

    session.pop(
        "chat_id",
        None
    )

    obter_chat_usuario(
        usuario["id"]
    )

    return redirect(
        url_for("inicio")
    )


# ==========================================
# LOGIN COM GOOGLE
# ==========================================

@app.route("/login/google")
def login_google():

    redirect_uri = url_for(
        "google_callback",
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )


# ==========================================
# RETORNO DO GOOGLE
# ==========================================

@app.route("/login/google/callback")
def google_callback():

    try:

        token = google.authorize_access_token()

    except Exception as erro:

        print(
            "Erro no login Google:",
            erro
        )

        return (
            "Não foi possível realizar o login "
            "com Google."
        )

    userinfo = token.get("userinfo")

    if not userinfo:

        try:

            userinfo = google.userinfo(
                token=token
            )

        except Exception as erro:

            print(
                "Erro ao obter dados do Google:",
                erro
            )

            return (
                "O Google não retornou os dados "
                "do usuário."
            )

    email = userinfo.get("email")

    nome = userinfo.get("name")

    if not email:

        return (
            "O Google não retornou um e-mail."
        )

    email = email.strip().lower()

    if not nome:

        nome = email.split("@")[0]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT *
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    )

    usuario = cursor.fetchone()

    if usuario is None:

        senha_aleatoria = secrets.token_urlsafe(
            32
        )

        senha_hash = generate_password_hash(
            senha_aleatoria
        )

        try:

            cursor.execute(
                """
                INSERT INTO usuarios
                (nome, email, senha_hash)
                VALUES (?, ?, ?)
                """,
                (
                    nome,
                    email,
                    senha_hash
                )
            )

            conexao.commit()

            usuario_id = cursor.lastrowid

        except Exception as erro:

            print(
                "Erro ao criar conta Google:",
                erro
            )

            conexao.close()

            return (
                "Não foi possível criar "
                "sua conta Google."
            )

    else:

        usuario_id = usuario["id"]

    conexao.close()

    session["usuario_id"] = usuario_id

    session["usuario_nome"] = nome

    session["usuario_email"] = email

    session.pop(
        "chat_id",
        None
    )

    obter_chat_usuario(
        usuario_id
    )

    return redirect(
        url_for("inicio")
    )


# ==========================================
# TESTE DO RESEND
# ==========================================

@app.route("/teste-email")
def teste_email():

    try:

        resend.Emails.send(
            {
                "from": "Estuda IA <onboarding@resend.dev>",
                "to": ["estudaiagmail@gmail.com"],
                "subject": "Teste - Estuda IA",
                "html": """
                    <h2>Estuda IA</h2>

                    <p>
                        Se você recebeu este e-mail,
                        o envio está funcionando!
                    </p>
                """
            }
        )

        return "E-mail enviado com sucesso!"

    except Exception as erro:

        print(
            "ERRO AO ENVIAR E-MAIL:",
            erro
        )

        return f"Erro ao enviar e-mail: {erro}"


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==========================================
# INICIAR SERVIDOR
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )