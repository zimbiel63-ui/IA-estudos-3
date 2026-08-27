import ast
import operator
import re
import os

from dotenv import load_dotenv
from google import genai

from busca import buscar_conteudo


# ============================================================
# CONFIGURAÇÃO DO GEMINI
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY não encontrada no arquivo .env"
    )

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# GEMINI — CÉREBRO DO ESTUDA IA
# ============================================================

def perguntar_gemini(
    pergunta,
    historico=None,
    contexto=""
):

    if historico is None:
        historico = []

    prompt = """
Você é o professor virtual do Estuda IA.

Seu objetivo é ajudar estudantes a aprender.

REGRAS:

1. Explique de forma clara e adequada para estudantes.
2. Não invente informações.
3. Quando a pergunta for matemática, ensine o raciocínio passo a passo.
4. Não entregue simplesmente a resposta de um exercício quando o aluno
   estiver tentando aprender. Ajude com pistas e etapas.
5. Use o histórico da conversa para entender o contexto.
6. Se o aluno fizer uma pergunta relacionada à mensagem anterior,
   continue o raciocínio em vez de começar tudo novamente.
7. Se o aluno mudar de assunto, acompanhe a mudança.
8. Não diga que você é uma pessoa.
9. Não invente que pesquisou algo se não recebeu conteúdo de pesquisa.
10. Seja natural e converse com o aluno.
11. Não use respostas programadas quando puder responder usando o Gemini.
12. O conteúdo encontrado pela busca deve servir como contexto para sua
    resposta, não como uma resposta pronta.
13. Para exercícios escolares, priorize ensinar o raciocínio.
14. Se o aluno estiver claramente pedindo apenas uma explicação de um
    conceito, explique normalmente.
15. Não diga que utilizou uma fonte se ela não estiver no conteúdo fornecido.

HISTÓRICO DA CONVERSA:
"""

    for mensagem in historico:

        pergunta_anterior = mensagem.get(
            "pergunta",
            ""
        )

        resposta_anterior = mensagem.get(
            "resposta",
            ""
        )

        prompt += f"""

Aluno:
{pergunta_anterior}

Professor:
{resposta_anterior}

"""

    if contexto:

        prompt += f"""

CONTEÚDO ENCONTRADO PELA BUSCA:
{contexto}

"""

    prompt += f"""

NOVA PERGUNTA DO ALUNO:
{pergunta}

Responda como o professor do Estuda IA.
"""

    try:

        resposta = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if resposta.text:
            return resposta.text.strip()

        return (
            "Não consegui gerar uma resposta agora. "
            "Tente novamente."
        )

    except Exception as erro:

        print(
            "ERRO GEMINI:",
            erro
        )

        return (
            "Tive um problema ao conversar "
            "com o Gemini. Tente novamente."
        )


# ============================================================
# OPERADORES MATEMÁTICOS PERMITIDOS
# ============================================================

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow
}


# ============================================================
# CALCULADORA SEGURA
# ============================================================

def calcular_expressao(expressao):

    try:

        arvore = ast.parse(
            expressao,
            mode="eval"
        )

        def calcular(no):

            if isinstance(no, ast.Expression):
                return calcular(no.body)

            if isinstance(no, ast.Constant):

                if isinstance(no.value, (int, float)):
                    return no.value

                raise ValueError

            if isinstance(no, ast.BinOp):

                operador = OPERADORES.get(
                    type(no.op)
                )

                if operador is None:
                    raise ValueError

                esquerda = calcular(no.left)
                direita = calcular(no.right)

                return operador(
                    esquerda,
                    direita
                )

            if isinstance(no, ast.UnaryOp):

                valor = calcular(no.operand)

                if isinstance(no.op, ast.USub):
                    return -valor

                if isinstance(no.op, ast.UAdd):
                    return valor

                raise ValueError

            raise ValueError

        return calcular(arvore)

    except Exception:
        return None


# ============================================================
# PREPARAR MATEMÁTICA
# ============================================================

def preparar_matematica(pergunta):

    texto = pergunta.lower()

    texto = texto.replace(",", ".")

    substituicoes = {
        "vezes": "*",
        "multiplicado por": "*",
        "multiplicado": "*",
        "dividido por": "/",
        "dividido": "/",
        "mais": "+",
        "menos": "-"
    }

    for antigo, novo in substituicoes.items():

        texto = texto.replace(
            antigo,
            novo
        )

    frases = [
        "quanto é",
        "quanto e",
        "qual é",
        "qual e",
        "calcule",
        "calcula",
        "resolva",
        "resolver",
        "resultado de",
        "me diga",
        "me fala"
    ]

    for frase in frases:

        texto = texto.replace(
            frase,
            ""
        )

    texto = re.sub(
        r"[^0-9+\-*/().% ]",
        "",
        texto
    )

    return texto.strip()


# ============================================================
# IDENTIFICAR CONTA NUMÉRICA
# ============================================================

def identificar_conta(pergunta):

    expressao = preparar_matematica(
        pergunta
    )

    if not expressao:
        return None

    if not re.search(
        r"[+\-*/%]",
        expressao
    ):
        return None

    if not re.search(
        r"\d",
        expressao
    ):
        return None

    return expressao


# ============================================================
# IDENTIFICAR ASSUNTO DE MATEMÁTICA
# ============================================================

def identificar_assunto_matematica(pergunta):

    texto = pergunta.lower()

    assuntos = {

        "frações": [
            "fração",
            "frações",
            "fracao",
            "fracoes"
        ],

        "porcentagem": [
            "porcentagem",
            "percentual",
            "%"
        ],

        "razão e proporção": [
            "razão",
            "razao",
            "proporção",
            "proporcao"
        ],

        "regra de três": [
            "regra de três",
            "regra de tres"
        ],

        "potenciação": [
            "potência",
            "potencia",
            "potenciação",
            "potenciacao",
            "expoente"
        ],

        "radiciação": [
            "raiz",
            "radiciação",
            "radiciacao"
        ],

        "expressões algébricas": [
            "expressão algébrica",
            "expressao algebrica",
            "expressões algébricas",
            "expressoes algebricas"
        ],

        "equação do 1º grau": [
            "equação do 1",
            "equacao do 1",
            "primeiro grau",
            "1º grau"
        ],

        "equação do 2º grau": [
            "equação do 2",
            "equacao do 2",
            "segundo grau",
            "2º grau",
            "bhaskara",
            "delta"
        ],

        "sistemas": [
            "sistema de equações",
            "sistema de equacoes",
            "sistemas"
        ],

        "produtos notáveis": [
            "produto notável",
            "produto notavel",
            "produtos notáveis",
            "produtos notaveis"
        ],

        "fatoração": [
            "fatoração",
            "fatoracao",
            "fatorar"
        ],

        "teorema de pitágoras": [
            "pitágoras",
            "pitagoras",
            "hipotenusa"
        ],

        "área e volume": [
            "área",
            "area",
            "volume",
            "perímetro",
            "perimetro"
        ],

        "estatística": [
            "estatística",
            "estatistica",
            "média",
            "media",
            "mediana",
            "moda"
        ],

        "probabilidade": [
            "probabilidade",
            "chance"
        ]
    }

    for assunto, palavras in assuntos.items():

        for palavra in palavras:

            if palavra in texto:
                return assunto

    return None


# ============================================================
# CONTEÚDOS MATEMÁTICOS
# ============================================================

CONTEUDOS = {

    "frações": """
Frações representam uma divisão entre dois números.

O número de cima é o numerador e o número de baixo é
o denominador.

Para somar ou subtrair frações com denominadores diferentes,
primeiro precisamos encontrar um denominador comum.
""",

    "porcentagem": """
Porcentagem representa uma razão cujo denominador é 100.

25% = 25/100 = 0,25

A porcentagem pode representar aumentos, descontos
e partes de uma quantidade.
""",

    "razão e proporção": """
Razão é uma comparação entre duas grandezas.

Uma proporção acontece quando duas razões são equivalentes.

Antes de calcular, precisamos identificar quais grandezas
estão sendo comparadas.
""",

    "regra de três": """
A regra de três pode ser utilizada quando existe uma relação
entre grandezas.

Primeiro identificamos as grandezas e organizamos os valores.

Depois verificamos se a relação é direta ou inversamente
proporcional.
""",

    "potenciação": """
Uma potência possui uma base e um expoente.

O expoente indica quantas vezes a base participa
da multiplicação.

Também existem propriedades importantes das potências.
""",

    "radiciação": """
A radiciação está relacionada à potenciação.

Por exemplo:

√9 = 3

porque:

3² = 9

Também podemos simplificar algumas raízes.
""",

    "expressões algébricas": """
Expressões algébricas utilizam números, letras e operações.

Devemos identificar termos semelhantes e respeitar
a ordem das operações.
""",

    "equação do 1º grau": """
Uma equação do primeiro grau pode ser representada por:

ax + b = 0

O objetivo é descobrir o valor da incógnita preservando
a igualdade.
""",

    "equação do 2º grau": """
A forma geral é:

ax² + bx + c = 0

Podemos utilizar o discriminante:

Delta = b² - 4ac

Depois podemos utilizar a fórmula de Bhaskara.
""",

    "sistemas": """
Um sistema representa condições que precisam ser satisfeitas
simultaneamente.

Podemos utilizar substituição, adição ou comparação.
""",

    "produtos notáveis": """
Os produtos notáveis são identidades algébricas que permitem
desenvolver determinadas expressões rapidamente.

É importante reconhecer a estrutura da expressão.
""",

    "fatoração": """
Fatorar significa escrever uma expressão como produto
de fatores.

Um método inicial é colocar o fator comum em evidência.
""",

    "teorema de pitágoras": """
Em um triângulo retângulo:

a² = b² + c²

A hipotenusa é o lado oposto ao ângulo de 90 graus
e é o maior lado.
""",

    "área e volume": """
Área representa a medida de uma superfície.

Volume representa o espaço ocupado por um sólido.

Primeiro precisamos identificar qual figura ou sólido
está sendo analisado.
""",

    "estatística": """
A média aritmética é calculada pela soma dos valores
dividida pela quantidade de valores.

A mediana é o valor central dos dados ordenados.

A moda é o valor que aparece com maior frequência.
""",

    "probabilidade": """
Quando todos os resultados são igualmente prováveis:

P(A) = casos favoráveis / casos possíveis

Primeiro precisamos identificar o espaço amostral.
"""
}


# ============================================================
# EXPLICAÇÃO INICIAL
# ============================================================

def iniciar_assunto_matematica(assunto):

    conteudo = CONTEUDOS.get(
        assunto
    )

    if not conteudo:

        conteudo = (
            "Vamos estudar esse assunto passo a passo."
        )

    return (
        "Professor de Matemática - 9º ano\n\n"
        f"Assunto: {assunto.title()}\n\n"
        f"{conteudo}\n\n"
        "Agora é sua vez.\n\n"
        "Eu não vou simplesmente entregar a resposta.\n"
        "Quero entender como você está pensando.\n\n"
        "Qual seria o primeiro passo para resolver "
        "esse tipo de problema?"
    )


# ============================================================
# DICAS
# ============================================================

def gerar_dica(assunto):

    dicas = {

        "frações":
            "Observe os denominadores. Eles são iguais ou diferentes?",

        "porcentagem":
            "Transforme a porcentagem em decimal ou fração sobre 100.",

        "razão e proporção":
            "Compare as duas grandezas antes de montar a proporção.",

        "regra de três":
            "Identifique primeiro quais grandezas estão relacionadas.",

        "potenciação":
            "Observe a base e o expoente e procure uma propriedade.",

        "radiciação":
            "Procure fatores dentro da raiz que formem quadrados perfeitos.",

        "expressões algébricas":
            "Separe termos semelhantes antes de realizar as operações.",

        "equação do 1º grau":
            "Tente eliminar primeiro o termo que acompanha a incógnita.",

        "equação do 2º grau":
            "Antes de usar Bhaskara, identifique corretamente a, b e c.",

        "sistemas":
            "Veja qual das equações permite isolar uma incógnita com mais facilidade.",

        "produtos notáveis":
            "Compare a estrutura da expressão com as identidades conhecidas.",

        "fatoração":
            "Procure primeiro por um fator comum aos termos.",

        "teorema de pitágoras":
            "Identifique a hipotenusa antes de substituir qualquer valor.",

        "área e volume":
            "Identifique primeiro qual figura ou sólido está sendo analisado.",

        "estatística":
            "Organize os dados antes de calcular média, mediana ou moda.",

        "probabilidade":
            "Conte primeiro quantos resultados possíveis existem."
    }

    return dicas.get(
        assunto,
        "Divida o problema em etapas menores."
    )


# ============================================================
# ANALISAR TENTATIVA
# ============================================================

def analisar_tentativa(
    pergunta,
    session
):

    assunto = session.get(
        "assunto_matematica"
    )

    tentativa = pergunta.lower().strip()

    if tentativa in [
        "não sei",
        "nao sei",
        "não consigo",
        "nao consigo",
        "me dá a resposta",
        "me da a resposta"
    ]:

        session["dicas"] = session.get(
            "dicas",
            0
        ) + 1

        return (
            "Tudo bem. Errar e não saber faz parte do aprendizado.\n\n"
            f"Dica: {gerar_dica(assunto)}\n\n"
            "Tente novamente. Quero ver seu raciocínio."
        )

    session["tentativas"] = session.get(
        "tentativas",
        0
    ) + 1

    if assunto == "equação do 1º grau":

        if any(
            palavra in tentativa
            for palavra in [
                "subtrair",
                "tirar",
                "diminuir"
            ]
        ):

            return (
                "Boa ideia.\n\n"
                "Você percebeu que precisamos eliminar "
                "um termo da equação.\n\n"
                "Tudo que fazemos de um lado da igualdade "
                "precisamos fazer do outro lado também.\n\n"
                "Qual operação você faria nos dois lados?"
            )

        if "dividir" in tentativa:

            return (
                "Você já está pensando no isolamento da incógnita.\n\n"
                "Mas verifique se ainda existe algum termo "
                "somando ou subtraindo junto do x.\n\n"
                "O que você precisa eliminar primeiro?"
            )

    if assunto == "equação do 2º grau":

        if any(
            palavra in tentativa
            for palavra in [
                "a =",
                "a é",
                "a:",
                "b =",
                "b é",
                "b:",
                "c =",
                "c é",
                "c:"
            ]
        ):

            return (
                "Muito bem. Identificar os coeficientes "
                "é uma etapa essencial.\n\n"
                "Agora confira se a equação realmente está "
                "na forma:\n\n"
                "ax² + bx + c = 0\n\n"
                "Quais são os valores de a, b e c?"
            )

        if "delta" in tentativa:

            return (
                "Exatamente. O próximo conceito importante "
                "é o discriminante.\n\n"
                "A fórmula é:\n\n"
                "Delta = b² - 4ac\n\n"
                "Agora tente substituir os valores de "
                "a, b e c na fórmula."
            )

    return (
        "Interessante. Vamos analisar seu raciocínio.\n\n"
        "Ainda não vou entregar a resposta.\n\n"
        f"Pista: {gerar_dica(assunto)}\n\n"
        "Tente novamente mostrando o próximo passo."
    )


# ============================================================
# PROFESSOR PRINCIPAL
# ============================================================

def responder_pergunta(
    pergunta,
    session=None,
    historico=None
):

    if not pergunta:
        return (
            "Escreva uma pergunta para eu poder ajudar."
        )

    pergunta = pergunta.strip()

    if session is None:
        session = {}

    if historico is None:
        historico = []

    contexto_conversa = ""

    for mensagem in historico:

        contexto_conversa += (
            f"Aluno: {mensagem.get('pergunta', '')}\n"
            f"Professor: {mensagem.get('resposta', '')}\n\n"
        )

    if session.get("assunto_matematica"):

        assunto = session[
            "assunto_matematica"
        ]

        novo_assunto = identificar_assunto_matematica(
            pergunta
        )

        if novo_assunto and novo_assunto != assunto:

            session["assunto_matematica"] = novo_assunto
            session["tentativas"] = 0
            session["dicas"] = 0

            return iniciar_assunto_matematica(
                novo_assunto
            )

        return analisar_tentativa(
            pergunta,
            session
        )

    assunto = identificar_assunto_matematica(
        pergunta
    )

    if assunto:

        session["assunto_matematica"] = assunto
        session["tentativas"] = 0
        session["dicas"] = 0

        return iniciar_assunto_matematica(
            assunto
        )

    expressao = identificar_conta(
        pergunta
    )

    if expressao:

        resultado = calcular_expressao(
            expressao
        )

        if resultado is not None:

            return perguntar_gemini(
                pergunta,
                historico,
                ""
            )

    try:

        conteudo = buscar_conteudo(
            pergunta
        )

    except Exception as erro:

        print(
            "Erro ao buscar conteúdo:",
            erro
        )

        conteudo = ""

    return perguntar_gemini(
        pergunta,
        historico,
        conteudo
    )