import discord
import os
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL = "llama3.2:latest"
PERSONA_PATH = "persona/new-persona.txt"

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
    print(f"Using Model: {MODEL} and Persona: {PERSONA_PATH}")

# Respond to messages
@client.event
async def on_message(message):
    if message.author.display_name == "Jay":
        return
    
    print(f"Received message from {message.author.display_name}: {message.content}")

    # get message history for context
    history = await get_message_history(message.channel, limit=10)

    prompt = create_prompt(history)

    print(f"Generated Prompt:\n{prompt}")

    # Only send the typing indicator if the bot is mentioned, otherwise just respond
    if "jay" in message.content.lower():
        async with message.channel.typing():   # <── typing indicator
            reply = await ask_llm(prompt)
    else:
        reply = await ask_llm(prompt)

    # Handle special commands
    if "$NO_COMMENT" in reply or "NO_COMMENT" in reply:
        print(reply)
        return
    elif "$THUMBS_UP" in reply:
        print("Reacted with 👍")
        await message.add_reaction("👍")
    elif "$THUMBS_DOWN" in reply:
        print("Reacted with 👎")
        await message.add_reaction("👎")
    else:
        print(f"Responded with: {reply}")
        await message.channel.send(reply)

# Load last 10 messages for context
async def get_message_history(channel, limit=10):
    messages = []
    async for msg in channel.history(limit=limit):
        if msg.embeds:
            for embed in msg.embeds:
                messages.append(f"{msg.author.display_name}: {embed.author.name}")
        else:
            messages.append(f"{msg.author.display_name}: {msg.content}")
    messages.reverse()  # Oldest first
    return '\n'.join(messages)

# Create the prompt for the LLM
def create_prompt(history):
    with open(PERSONA_PATH, "r") as F:
        persona = F.read()
    prompt = f"{persona}\n{history}\nJay:"
    return prompt

# Start the bot
client.run(os.getenv("DISCORD_TOKEN"))
