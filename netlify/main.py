from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Pergunta(BaseModel):
    message: str

contador_requisicoes = 0
LIMITE = 100

@app.post("/chat")
def chat(pergunta: Pergunta):

    global contador_requisicoes
    contador_requisicoes += 1

    # bloqueio simples
    if contador_requisicoes > LIMITE:
        return {"reply": "Limite de uso atingido por hoje 😅"}

    # Ler CSV
    df = pd.read_csv("historico_financeiro.csv")

    # Converter datas
    df["data"] = pd.to_datetime(df["data"])

    # Filtrar mês
    mes_mais_recente = df["data"].dt.month.max()
    df_mes = df[df["data"].dt.month == mes_mais_recente]

    # Calcular
    entradas = df_mes[df_mes["tipo"] == "Entrada"]["valor"].sum()
    saidas = df_mes[df_mes["tipo"] == "Saída"]["valor"].sum()
    saldo = entradas + saidas

    gastos_categoria = (
    df_mes[df_mes["tipo"] == "Saída"]
    .groupby("categoria")["valor"]
    .sum()
    .abs()
    .sort_values(ascending=False)
    )

    if not gastos_categoria.empty:
        maior_categoria = gastos_categoria.idxmax()
        maior_valor = gastos_categoria.max()
    else:
        maior_categoria = "nenhuma categoria"
        maior_valor = 0 

    # Montar resposta em texto
    prompt = f"""
    Você é um assistente financeiro pessoal.

    Dados do usuário:
    - Entradas: {entradas:.2f}
    - Saídas: {abs(saidas):.2f}
    - Saldo: {saldo:.2f}
    - Maior gasto: {maior_categoria} (R$ {maior_valor:.2f})

    Pergunta do usuário:
    {pergunta.message}

    Responda de forma:
    - Consultiva
    - Levemente descontraída
    - Educativa
    - Direta
    - Traga sugestões práticas
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": "Você é um especialista em finanças pessoais."},
                {"role": "user", "content": prompt}
            ]
        )

        resposta = response.choices[0].message.content

    except Exception as e:
        resposta = "Tive um problema ao analisar seus dados 😢. Tente novamente."
        print(e)

    resposta = response.choices[0].message.content

    return {
    "reply": resposta
        }
