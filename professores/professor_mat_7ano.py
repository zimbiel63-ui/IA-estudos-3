# Professor de Matemática - 7º Ano
# Estuda IA


conteudos = {


    "numeros_inteiros": [
        "números inteiros",
        "positivo",
        "negativo",
        "oposto"
    ],


    "operacoes": [
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


    "numeros_decimais": [
        "decimal",
        "vírgula"
    ],


    "porcentagem": [
        "porcentagem",
        "%"
    ],


    "razao_proporcao": [
        "razão",
        "proporção"
    ],


    "regra_de_tres": [
        "regra de três",
        "regra de tres"
    ],


    "potenciacao": [
        "potência",
        "expoente",
        "base"
    ],


    "expressao_algebrica": [
        "expressão algébrica",
        "letra",
        "variável"
    ],


    "equacao": [
        "equação",
        "incógnita",
        "valor de x"
    ],


    "plano_cartesiano": [
        "plano cartesiano",
        "coordenada",
        "ponto"
    ],


    "geometria": [
        "ângulo",
        "triângulo",
        "polígono"
    ],


    "area_perimetro": [
        "área",
        "perímetro"
    ],


    "circunferencia": [
        "círculo",
        "circunferência",
        "raio"
    ],


    "volume": [
        "volume",
        "sólido geométrico"
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



def responder_matematica_7(pergunta):


    assunto = identificar_assunto(pergunta)


    if assunto:


        return (
            "📚 Professor de Matemática 7º ano\n\n"
            f"Assunto identificado: {assunto}\n\n"
            "Vamos aprender passo a passo."
        )


    return None