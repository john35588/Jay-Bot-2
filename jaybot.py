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

    prompt = create_prompt(history)

    async with message.channel.typing():   # <── typing indicator
        reply = await ask_llm(prompt)

    await message.channel.send(reply)

# Load last 10 messages for context
async def get_message_history(channel, limit=10):
    messages = []
    async for msg in channel.history(limit=limit):
        messages.append(f"{msg.author.name}: {msg.content}")
    messages.reverse()  # Oldest first
    return '/n'.join(messages)

# Create a good prompt for the LLM
def create_prompt(history):
    with open("persona/jay-persona.txt", "r") as F:
        persona = F.read()
    prompt = f"{persona}\n\nRecent conversation:\n{history}\n\nJay's response:"
    return prompt

# Start the bot
client.run(os.getenv("DISCORD_TOKEN"))
