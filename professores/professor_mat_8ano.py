# Professor de Matemática - 8º Ano
# Estuda IA


conteudos = {

    "numeros_operacoes": [
        "números",
        "operações",
        "conta",
        "decimal"
    ],


    "fracoes": [
        "fração",
        "frações",
        "número racional"
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


    "monomios_polinomios": [
        "monômio",
        "polinômio",
        "termos semelhantes"
    ],


    "produtos_notaveis": [
        "produto notável",
        "quadrado da soma",
        "quadrado da diferença"
    ],


    "fatoracao": [
        "fatoração",
        "fatorar"
    ],


    "equacao_primeiro_grau": [
        "equação",
        "incógnita",
        "resolver x"
    ],


    "sistemas": [
        "sistema",
        "duas equações"
    ],


    "plano_cartesiano": [
        "plano cartesiano",
        "coordenada",
        "ponto"
    ],


    "geometria": [
        "ângulo",
        "triângulo",
        "figura geométrica"
    ],


    "area_perimetro": [
        "área",
        "perímetro"
    ],


    "volume": [
        "volume",
        "cubo",
        "paralelepípedo"
    ],


    "estatistica": [
        "média",
        "moda",
        "mediana",
        "gráfico"
    ],


    "probabilidade": [
        "probabilidade",
        "chance"
    ]

}



def identificar_assunto(pergunta):

    pergunta = pergunta.lower()


    for assunto, palavras in conteudos.items():

        for palavra in palavras:

            if palavra in pergunta:

                return assunto


    return None



def responder_matematica_8(pergunta):


    assunto = identificar_assunto(pergunta)


    if assunto:

        return (
            "📚 Professor de Matemática 8º ano\n\n"
            f"Assunto identificado: {assunto}\n\n"
            "Vamos aprender passo a passo."
        )


    return None