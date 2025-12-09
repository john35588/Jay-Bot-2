import discord
import os
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL = "llama3.2:latest"
GENERAL_PERSONA_PATH = "persona/new-persona.txt"
MINECRAFT_PERSONA_PATH = "persona/minecraft-persona.txt"
MENTIONED_PERSONA_PATH = "persona/mentioned-persona.txt"

# Function to interact with the LLM
async def ask_llm(prompt: str):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    # Make the HTTP request to the LLM server
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            data = await resp.json()
            return data["response"]

# Bot is ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print(f"Using Model: {MODEL} and Persona: {GENERAL_PERSONA_PATH}")

# Respond to messages
@client.event
async def on_message(message):

    # Determine the prompt based on the message context
    if message.author.display_name == "Jay": # Do not respond to self
        return
    elif "minecraft" in message.channel.name.lower(): # Alternate prompt for Minecraft channel
        history = await get_message_history(message.channel, limit=10)
        prompt = minecraft_prompt(history)
    elif "jay" in message.content.lower(): # Alternate prompt if mentioned
        history = await get_message_history(message.channel, limit=10)
        prompt = mentioned_prompt(history)
    else: # Default prompt for all other messages
        history = await get_message_history(message.channel, limit=10)
        prompt = general_prompt(history)

    if prompt:
        reply = await ask_llm(prompt)

    # Handle special commands for reactions or declining to comment
    if "$NO_COMMENT" in reply or "NO_COMMENT" in reply:
        print(reply)
        return
    elif "$THUMBS_UP" in reply or "THUMBS_UP" in reply:
        print("Reacted with 👍")
        await message.add_reaction("👍")
    elif "$THUMBS_DOWN" in reply or "THUMBS_DOWN" in reply:
        print("Reacted with 👎")
        await message.add_reaction("👎")
    elif "$HEART" in reply or "HEART" in reply:
        print("Reacted with ❤️")
        await message.add_reaction("❤️")
    else:
        print(f"Responded with: {reply}")
        await message.channel.send(reply)

    print()

# Load last 10 messages from the Minecraft channel for context
async def get_message_history(channel, limit=10):
    messages = []
    async for msg in channel.history(limit=limit):
        if msg.embeds: # Handle embedded messages (Minecraft death messages)
            for embed in msg.embeds:
                messages.append(embed.author.name)
        elif "minecraft-bridge" in msg.author.display_name.lower(): # Special handling for minecraft-bridge messages
            content = msg.content
            if "»" in content: # Split username and message
                content = content.split(" » ", 1)
                messages.append(f"{content[0]}: {content[1]}")
            else: # Server status messages, etc.
                messages.append(content)
        else: # Regular messages
            messages.append(f"{msg.author.display_name}: {msg.content}")

    messages.reverse()  # Oldest first
    print(f"Loaded message history for context:\n{'\n'.join(messages)}\n")
    return '\n'.join(messages)

# Create the Minecraft server prompt
def minecraft_prompt(history):
    with open(MINECRAFT_PERSONA_PATH, "r") as F:
        persona = F.read()
    prompt = f"{persona}\n{history}\nJay:"
    return prompt

# Create the mentioned prompt
def mentioned_prompt(history):
    with open(MENTIONED_PERSONA_PATH, "r") as F:
        persona = F.read()
    prompt = f"{persona}\n{history}\nJay:"
    return prompt

# Create the general purpose prompt
def general_prompt(history):
    with open(GENERAL_PERSONA_PATH, "r") as F:
        persona = F.read()
    prompt = f"{persona}\n{history}\nJay:"
    return prompt

# Start the bot
client.run(os.getenv("DISCORD_TOKEN"))