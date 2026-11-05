import discord
import os
import ai
import logging
from dotenv import load_dotenv
from datetime import datetime
from discord import app_commands
from discord.ext import commands, tasks

load_dotenv()

GUILD_ID = os.getenv("GUILD_ID")
if GUILD_ID is None:
    raise ValueError("Invalid GUILD_ID")

CHANNEL_ID = os.getenv("CHANNEL_ID")

# Guild ID for testing server
TEST_GUILD = discord.Object(id=GUILD_ID)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Permissions
intents = discord.Intents.default()  # Sets default permissions
intents.members = True  # Enables access to member data
intents.message_content = True  # Allows bot to read messages (required for most bots)
intents.presences = True  # Allows bot to see online/offline status
bot = commands.Bot(command_prefix='hai ', intents=intents)



def run() -> None:
    """Runs the bot (starts a blocking async loop)"""

    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise ValueError("Invalid discord token")

    bot.run(TOKEN)


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
    # Immediately sync slash commands with guild
    bot.tree.copy_global_to(guild=TEST_GUILD)
    await bot.tree.sync(guild=TEST_GUILD)

    # Starts the cron job
    auto_loop.start()

    print(f'{bot.user} has connected to Discord')


@bot.tree.command(name="info", description="Displays the full overview and status")
async def info(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(f"Model: __**{ai.MODEL}**__")

@bot.tree.command(name="change_model", description="Switch the AI model")
async def change_model(interaction: discord.Interaction, model: str) -> None:
    ai.MODEL = model
    logger.info("AI model changed to " + model)
    await interaction.response.send_message(f"AI model changed to **{model}**")

@bot.tree.command(name="load_memory", description="Load a specific memory file")
async def load_memory(interaction: discord.Interaction, filepath: str) -> None:
    ai.messages = ai.load_memory(filepath)
    logger.info("New memories loaded at " + filepath)
    await interaction.response.send_message(f"New memories loaded at *{filepath}*")

@bot.tree.command(name="backup_memory", description="Backup the current memory file")
async def backup_memory(interaction: discord.Interaction, filename: str) -> None:
    filepath = "sessions/messages/" + filename
    ai.dump_memory(filepath)
    logger.info("Current memory backed up at " + filepath)
    await interaction.response.send_message(f"Current memory backed up at *{filepath}*")


@bot.tree.command(name="reflect", description="Trigger agent reflection")
async def reflect(interaction: discord.Interaction) -> None:
    await ai.reflect()
    return


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    if message.content.split()[0] != 'hai':
        return
    user_input = message.content[4:]
    formatted_input = f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ({str(message.author)}) {user_input}"

    logger.info(formatted_input)

    # Iterates over the get_response async generator
    async for response_message, response_reasoning in ai.get_response(formatted_input):
        # If model did a tool call
        if response_message == "tool_call":
            logger.info("Bot: " + response_reasoning)
        else:  # No tool call, normal output
            if response_reasoning:
                logger.info("Reasoning: " + response_reasoning)
            logger.info("Bot: " + response_message)

            await split_and_send(response_message, message.channel)


# Auto loop tasks
@tasks.loop(minutes=1)
async def auto_loop() -> None:
    CHANNEL_ID = os.getenv("CHANNEL_ID")
    if CHANNEL_ID is None:
        raise ValueError("Invalid GUILD_ID")
    channel = await bot.fetch_channel(int(CHANNEL_ID))
    
    system_input = "Running looping agent activation"
    print("Running cron job")

    formatted_input = f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] (System) {system_input}"
    
    logger.info(formatted_input)
    
    # Iterates over the get_response async generator
    async for response_message, response_reasoning in ai.get_response(formatted_input):
        # If model did a tool call
        if response_message == "tool_call":
            logger.info("Bot: " + response_reasoning)
        else:  # No tool call, normal output
            if response_reasoning:
                logger.info("Reasoning: " + response_reasoning)
            logger.info("Bot: " + response_message)

            if isinstance(channel, discord.abc.Messageable):
                await split_and_send(response_message, channel)
            else:
                raise TypeError("Channel does not support sending messages")

