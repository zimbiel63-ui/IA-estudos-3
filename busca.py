import wikipediaapi
import requests
import os

from entender import entender_pergunta


wiki = wikipediaapi.Wikipedia(
    language="pt",
    user_agent="IA-Estudos/1.0"
)


def nome_arquivo(assunto):

    caracteres_invalidos = '<>:"/\\|?*'

    for caractere in caracteres_invalidos:
        assunto = assunto.replace(caractere, "")

    assunto = assunto.replace(" ", "_")

    return assunto + ".txt"


def carregar_info(assunto):

    caminho = os.path.join(
        "InfoGoogle",
        nome_arquivo(assunto)
    )

    if os.path.exists(caminho):

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return arquivo.read()

    return None


def salvar_info(assunto, texto):

    if not os.path.exists("InfoGoogle"):
        os.makedirs("InfoGoogle")

    caminho = os.path.join(
        "InfoGoogle",
        nome_arquivo(assunto)
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(texto)


def procurar_wikipedia(assunto):

    try:

        pagina = wiki.page(assunto)

        if pagina.exists():
            return pagina

        url = "https://pt.wikipedia.org/w/api.php"

        parametros = {
            "action": "query",
            "list": "search",
            "srsearch": assunto,
            "format": "json"
        }

        resposta = requests.get(
            url,
            params=parametros,
            headers={
                "User-Agent": "IA-Estudos/1.0"
            },
            timeout=10
        )

        resposta.raise_for_status()

        dados = resposta.json()

        resultados = dados.get(
            "query",
            {}
        ).get(
            "search",
            []
        )

        if resultados:

            titulo = resultados[0]["title"]

            pagina = wiki.page(titulo)

            if pagina.exists():
                return pagina

    except Exception as erro:

        print("Erro ao pesquisar na Wikipédia:", erro)

    return None


def buscar_conteudo(pergunta):

    assunto = entender_pergunta(pergunta)

    print("Assunto pesquisado:", assunto)

    if not assunto:
        return ""

    memoria = carregar_info(assunto)

    if memoria:
        return memoria

    pagina = procurar_wikipedia(assunto)

    if pagina:

        resumo = pagina.summary[:2000]

        salvar_info(
            assunto,
            resumo
        )

        return resumo

    return ""