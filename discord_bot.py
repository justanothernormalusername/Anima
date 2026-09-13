import discord
import os
import ai
import logging
from dotenv import load_dotenv
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise Exception("Invalid discord token")

# Permissions
intents = discord.Intents.default()  # Sets default permissions
intents.members = True  # Enables access to member data
intents.message_content = True  # Allows bot to read messages (required for most bots)
intents.presences = True  # Allows bot to see online/offline status
bot = commands.Bot(command_prefix='hai ', intents=intents)


async def split_and_send(message_out: str, channel: discord.abc.Messageable) -> None:
    def split_discord_message(text: str, limit: int=1900) -> list:
        """Split a long text into Discord-safe message chunks."""
        if len(text) <= limit:
            return [text]

        chunks = []
        while text:
            if len(text) <= limit:
                chunks.append(text)
                break

            split_at = text.rfind("\n", 0, limit)
            if split_at == -1:
                split_at = text.rfind(" ", 0, limit)
            if split_at == -1:
                split_at = limit

            chunk = text[:split_at].rstrip()
            if not chunk:   
                chunk = text[:limit]
                split_at = limit

            chunks.append(chunk)
            text = text[split_at:].lstrip()

        return chunks

    if len(message_out) > 0:
        for chunk in split_discord_message(message_out):
            await channel.send(chunk)
    else:
        await channel.send(message_out)


@bot.event  # An event is an action done by the bot
async def on_ready() -> None:  # async is a function that runs in the background
    print(f'{bot.user} has connected to Discord')


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    if message.content.split()[0] != 'hai':
        return
    user_input = message.content[4:]
    formatted_input = str(message.author) + ": " + user_input

    logger.info(formatted_input)
    response_message, response_reasoning = await ai.get_response(formatted_input)
    logger.info("Reasoning: " + response_reasoning)
    logger.info("Bot: " + response_message)

    await split_and_send(response_message, message.channel)


bot.run(TOKEN)