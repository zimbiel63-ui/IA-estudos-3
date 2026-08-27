# Professor de Matemática - 9º Ano
# Estuda IA

import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)


# ============================================================
# CONTEÚDOS DO 9º ANO
# ============================================================

conteudos = {

    "numeros_operacoes": [
        "soma",
        "adição",
        "subtração",
        "multiplicação",
        "divisão",
        "conta"
    ],

    "fracoes": [
        "fração",
        "frações",
        "numerador",
        "denominador"
    ],

    "porcentagem": [
        "porcentagem",
        "%"
    ],

    "razao_proporcao": [
        "razão",
        "proporção"
    ],

    "regra_tres": [
        "regra de três",
        "regra de tres"
    ],

    "potenciacao": [
        "potência",
        "potencia",
        "expoente"
    ],

    "radiciacao": [
        "raiz",
        "raiz quadrada"
    ],

    "expressoes_algebricas": [
        "expressão algébrica",
        "expressao algebrica"
    ],

    "equacao_1_grau": [
        "equação do primeiro grau",
        "equação 1 grau"
    ],

    "equacao_2_grau": [
        "equação do segundo grau",
        "equação 2 grau",
        "bhaskara"
    ],

    "sistemas": [
        "sistema",
        "sistemas de equações"
    ],

    "produtos_notaveis": [
        "produto notável",
        "produto notavel",
        "quadrado da soma"
    ],

    "fatoracao": [
        "fatoração",
        "fatorar"
    ],

    "pitagoras": [
        "pitágoras",
        "pitagoras",
        "hipotenusa"
    ],

    "area_volume": [
        "área",
        "volume",
        "perímetro",
        "perimetro"
    ],

    "estatistica": [
        "média",
        "media",
        "mediana",
        "moda",
        "gráfico",
        "grafico"
    ],

    "probabilidade": [
        "probabilidade",
        "chance"
    ]
}


# ============================================================
# IDENTIFICAÇÃO DO ASSUNTO
# ============================================================

def identificar_assunto(pergunta):

    pergunta = pergunta.lower()

    for assunto, palavras in conteudos.items():

        for palavra in palavras:

            if palavra in pergunta:
                return assunto

    return None


# ============================================================
# EXTRAIR NÚMEROS
# ============================================================

def extrair_numeros(texto):

    numeros = re.findall(
        r"\d+(?:[.,]\d+)?",
        texto
    )

    return numeros


# ============================================================
# PREPARAR EXPRESSÃO MATEMÁTICA
# ============================================================

def preparar_expressao(texto):

    texto = texto.lower().strip()

    # Símbolos comuns
    texto = texto.replace("×", "*")
    texto = texto.replace("÷", "/")
    texto = texto.replace("−", "-")
    texto = texto.replace("–", "-")
    texto = texto.replace("^", "**")

    # Vírgula decimal
    texto = re.sub(
        r"(\d),(\d)",
        r"\1.\2",
        texto
    )

    # Raiz quadrada simples
    texto = re.sub(
        r"√\s*(\d+(?:\.\d+)?)",
        r"sqrt(\1)",
        texto
    )

    # x², x³ etc.
    texto = re.sub(
        r"([a-zA-Z0-9\)])²",
        r"\1**2",
        texto
    )

    texto = re.sub(
        r"([a-zA-Z0-9\)])³",
        r"\1**3",
        texto
    )

    # Remove espaços
    texto = texto.replace(" ", "")

    return texto


# ============================================================
# TENTAR INTERPRETAR MATEMÁTICA
# ============================================================

def interpretar_matematica(pergunta):

    texto = preparar_expressao(pergunta)

    # Só tenta interpretar se houver sinais de matemática
    sinais = [
        "+",
        "-",
        "*",
        "/",
        "**",
        "=",
        "√",
        "²",
        "³"
    ]

    tem_matematica = any(
        sinal in pergunta
        for sinal in sinais
    )

    tem_numero = bool(
        re.search(r"\d", pergunta)
    )

    if not tem_matematica or not tem_numero:
        return None


    transformacoes = (
        standard_transformations
        + (
            implicit_multiplication_application,
            convert_xor
        )
    )


    # ========================================================
    # EQUAÇÃO
    # ========================================================

    if "=" in texto:

        partes = texto.split("=")

        if len(partes) == 2:

            esquerda = partes[0]
            direita = partes[1]

            try:

                x = sp.Symbol("x")

                lado_esquerdo = parse_expr(
                    esquerda,
                    transformations=transformacoes
                )

                lado_direito = parse_expr(
                    direita,
                    transformations=transformacoes
                )

                equacao = sp.Eq(
                    lado_esquerdo,
                    lado_direito
                )

                solucoes = sp.solve(
                    equacao,
                    x
                )

                return {
                    "tipo": "equacao",
                    "expressao": equacao,
                    "solucoes": solucoes
                }

            except Exception:
                return None


    # ========================================================
    # EXPRESSÃO
    # ========================================================

    try:

        expressao = parse_expr(
            texto,
            transformations=transformacoes
        )

        resultado = sp.simplify(
            expressao
        )

        return {
            "tipo": "expressao",
            "expressao": expressao,
            "resultado": resultado
        }

    except Exception:

        return None


# ============================================================
# PROFESSOR
# ============================================================

def responder_matematica(pergunta):

    assunto = identificar_assunto(
        pergunta
    )


    # Primeiro tenta descobrir se existe uma conta
    matematica = interpretar_matematica(
        pergunta
    )


    # ========================================================
    # EQUAÇÃO DETECTADA
    # ========================================================

    if matematica and matematica["tipo"] == "equacao":

        return (
            "📚 Professor de Matemática 9º ano\n\n"
            "Entendi que você está trabalhando com uma equação.\n\n"
            "Não vou entregar a resposta de imediato. "
            "Vamos resolver juntos.\n\n"
            "Primeiro, observe a equação e tente identificar "
            "o que precisamos fazer para deixar a incógnita "
            "mais próxima de ficar sozinha.\n\n"
            "Qual seria o primeiro passo?"
        )


    # ========================================================
    # EXPRESSÃO DETECTADA
    # ========================================================

    if matematica and matematica["tipo"] == "expressao":

        return (
            "📚 Professor de Matemática 9º ano\n\n"
            "Entendi a expressão matemática.\n\n"
            "Antes de calcular, vamos organizar o raciocínio.\n\n"
            "Observe primeiro se existem parênteses, "
            "potências, multiplicações ou divisões.\n\n"
            "Qual dessas operações você acha que deve ser "
            "resolvida primeiro?"
        )


    # ========================================================
    # ASSUNTO NORMAL
    # ========================================================

    if assunto is None:

        return None


    explicacoes = {

        "numeros_operacoes":
        "Vamos trabalhar com números e operações. "
        "Primeiro vamos entender qual operação a questão está pedindo.",

        "fracoes":
        "Vamos aprender frações. "
        "Primeiro precisamos entender o papel do numerador e do denominador.",

        "porcentagem":
        "Vamos estudar porcentagem. "
        "Primeiro vamos entender qual parte do total está sendo representada.",

        "razao_proporcao":
        "Vamos analisar a relação entre grandezas usando razão e proporção.",

        "regra_tres":
        "Vamos montar a regra de três identificando primeiro "
        "quais são as grandezas envolvidas.",

        "potenciacao":
        "Vamos entender base e expoente antes de realizar a potência.",

        "radiciacao":
        "Vamos entender o que significa encontrar uma raiz "
        "antes de calcular.",

        "expressoes_algebricas":
        "Vamos organizar os termos da expressão algébrica "
        "antes de tentar calcular.",

        "equacao_1_grau":
        "Vamos trabalhar com a equação passo a passo, "
        "tentando deixar a incógnita sozinha.",

        "equacao_2_grau":
        "Vamos analisar a equação do segundo grau "
        "e descobrir qual método podemos utilizar.",

        "sistemas":
        "Vamos analisar as equações juntas "
        "e descobrir como encontrar as incógnitas.",

        "produtos_notaveis":
        "Vamos identificar o padrão do produto notável "
        "antes de desenvolver a expressão.",

        "fatoracao":
        "Vamos procurar uma forma de transformar "
        "a expressão em fatores.",

        "pitagoras":
        "Vamos identificar os lados do triângulo "
        "antes de escolher como aplicar o Teorema de Pitágoras.",

        "area_volume":
        "Vamos identificar a figura e as medidas "
        "antes de escolher a fórmula.",

        "estatistica":
        "Vamos analisar os dados e descobrir "
        "qual medida estatística a questão está pedindo.",

        "probabilidade":
        "Vamos identificar os resultados possíveis "
        "antes de calcular a probabilidade."
    }


    return (
        "📚 Professor de Matemática 9º ano\n\n"
        + explicacoes[assunto]
        + "\n\n"
        "Vamos resolver juntos. "
        "Primeiro me diga o que você entendeu da questão."
    )