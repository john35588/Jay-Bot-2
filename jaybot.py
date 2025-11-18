import discord
import os
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OLLAMA_URL = "http://192.168.86.2:30068/api/generate"
MODEL = "llama3.2:latest"

# Function to interact with the LLM
async def ask_llm(prompt: str):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            data = await resp.json()
            return data["response"]

# Bot is ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# Respond to messages
@client.event
async def on_message(message):
    if message.author.bot:
        return

    prompt = f"You are Jay, a friendly and humorous human in a Discord server. Respond to the following message casually and concisely:\n{message.content}\n"

    async with message.channel.typing():   # <── typing indicator
        reply = await ask_llm(prompt)

    await message.channel.send(reply)

# Start the bot
client.run(os.getenv("DISCORD_TOKEN"))
