import discord
import os
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OLLAMA_URL = "http://host.docker.internal:30068/api/generate"
MODEL = "qwen2.5:3b"   # change later if you want

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

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Right now: only reply when "jay" is mentioned
    if "jay" in message.content.lower():
        # Form a simple prompt
        prompt = f"Someone says to you: \"{message.content}\". Respond casually as if you are a human friend in a Discord chat."

        reply = await ask_llm(prompt)
        await message.channel.send(reply)

client.run(os.getenv("DISCORD_TOKEN"))
