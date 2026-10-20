import os
import discord
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHANNEL_GERAL_ID = int(os.getenv("CHANNEL_GERAL_ID", "0"))
CHANNEL_SDR_ID = int(os.getenv("CHANNEL_SDR_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot ativo e conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_message = message.content
    channel_id = message.channel.id

    # 1. Canal Geral -> Responde via Groq
    if channel_id == CHANNEL_GERAL_ID:
        response_text = call_groq(user_message)
        await message.channel.send(response_text)

    # 2. Canal SDR -> Responde via GLM (OpenRouter)
    elif channel_id == CHANNEL_SDR_ID:
        system_prompt = "Você é um agente de SDR especialista em prospecção, focado em conversão e follow-up humanizado."
        response_text = call_openrouter_glm(system_prompt, user_message)
        await message.channel.send(response_text)

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro na Groq: {str(e)}"

def call_openrouter_glm(system, prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "z-ai/glm-5:free",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro no GLM/OpenRouter: {str(e)}"

if __name__ == "__main__":
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
