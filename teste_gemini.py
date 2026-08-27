import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: GEMINI_API_KEY não encontrada.")
    exit()

client = genai.Client(api_key=api_key)

resposta = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explique o que é fotossíntese em poucas palavras."
)

print("\nRESPOSTA DO GEMINI:\n")
print(resposta.text)