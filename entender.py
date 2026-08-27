import unicodedata


def limpar_texto(texto):
    texto = texto.lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    )

    return texto


def entender_pergunta(pergunta):

    pergunta = limpar_texto(pergunta)

    palavras_remover = [
        "o que e",
        "o que foi",
        "quem foi",
        "me explique",
        "explique",
        "fale sobre",
        "me fala",
        "como funciona",
        "qual e",
        "qual foi"
    ]

    for palavra in palavras_remover:
        pergunta = pergunta.replace(
            palavra,
            ""
        )

    return pergunta.strip()


if __name__ == "__main__":

    pergunta = input(
        "Digite sua pergunta: "
    )

    assunto = entender_pergunta(pergunta)

    print("\nAssunto identificado:")
    print(assunto)