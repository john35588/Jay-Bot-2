import discord
import os
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OLLAMA_URL = "http://192.168.86.2:30068/api/generate"
MODEL = "llama3.2:latest"
NEWLINE = "\n"

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
    
    # get message history for context
    history = await get_message_history(message.channel, limit=10)

    # Construct prompt with persona and history
    prompt = f"You're Jay, a friendly and humorous bot in a Discord server. Here is the recent conversation:\n{NEWLINE.join(history)}\nCreate a short, witty response as Jay."

    print(f"Prompt sent to LLM: {prompt}")

    async with message.channel.typing():   # <── typing indicator
        reply = await ask_llm(prompt)

    await message.channel.send(reply)

# Load last 10 messages for context
async def get_message_history(channel, limit=10):
    messages = []
    async for msg in channel.history(limit=limit):
        messages.append(f"{msg.author.name}: {msg.content}")

# Start the bot
client.run(os.getenv("DISCORD_TOKEN"))
