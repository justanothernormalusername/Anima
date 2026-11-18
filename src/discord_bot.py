import discord
import os
import ai
import memory
import logging
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from discord.ext import commands, tasks

load_dotenv()

GUILD_ID = os.getenv("GUILD_ID")
if GUILD_ID is None:
    raise ValueError("Invalid GUILD_ID")

# Guild ID for testing server
TEST_GUILD = discord.Object(id=GUILD_ID)

discord.utils.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Permissions
intents = discord.Intents.default()  # Sets default permissions
intents.members = True  # Enables access to member data
intents.message_content = True  # Allows bot to read messages (required for most bots)
intents.presences = True  # Allows bot to see online/offline status
bot = commands.Bot(command_prefix='hai ', intents=intents)

CHANNEL_ID: int = int(os.getenv("CHANNEL_ID") or 0)
assert CHANNEL_ID, "Invalid CHANNEL_ID"

CHANNEL: discord.abc.Messageable | None = None




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

    # Cancels message if contains only whitespace/new lines
    if not message_out.strip():
        logger.warning("Model response content returned only whitespace, cancelling discord send")
        return

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

    # Sets the global channel variable
    global CHANNEL
    fetched_channel = bot.get_channel(CHANNEL_ID)
    if not isinstance(fetched_channel, discord.abc.Messageable):
        raise TypeError("Channel does not support sending messages")

    CHANNEL = fetched_channel

    # Starts the cron job
    # auto_loop.start()

    logger.info(f'{bot.user} has connected to Discord')


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
    memory.working_messages = memory.load_memory(filepath)
    logger.info("New memories loaded at " + filepath)
    await interaction.response.send_message(f"New memories loaded at *{filepath}*")

@bot.tree.command(name="backup_memory", description="Backup the current memory file")
async def backup_memory(interaction: discord.Interaction, directory_name: str) -> None:
    dir_path = Path("sessions/" + directory_name)
    dir_path.mkdir(parents=True, exist_ok=True)
    memory.dump_memory(memory.working_messages, str(dir_path) + "/", include_diary=True)
    logger.info("Current memory & diary backed up at " + str(dir_path))
    await interaction.response.send_message(f"Current memory backed up at *{dir_path}*")

@bot.tree.command(name="new_session", description="Create a new session with cleared memory and save_state.md imported")
async def new_session(interaction: discord.Interaction) -> None:
    memory.working_messages = memory.init_memory(True)
    logger.info("Memories cleared and save state appended")
    await interaction.response.send_message("Memories cleared and save state appended")

@bot.tree.command(name="run_reflection", description="Trigger agent reflection")
async def run_reflection(interaction: discord.Interaction) -> None:
    await auto_loop()
    await interaction.response.send_message("Running reflection loop")


async def chat_and_send(raw_input: str, messages: list, channel: discord.abc.Messageable) -> None:
    """Helper function that takes a raw input and sends the agent output to the channel"""
    logger.info(f"Raw input of {len(raw_input)} characters")
    logger.debug(f"User: {raw_input!r}")

    # Iterates over the get_response async generator
    async for response_message, response_reasoning in ai.get_response(messages, raw_input):
        # Only yields when a message needs to be send, tool calls stay local
        if response_reasoning:
            logger.debug(f"Reasoning: {response_reasoning!r}")
        logger.info(f"Response of {len(response_message)} characters")
        logger.debug(f"Bot: {response_message!r}")

        await split_and_send(response_message, channel)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    if message.content.split()[0] != 'hai':
        return
    user_input = message.content[4:]
    formatted_input = f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ({str(message.author)}) {user_input}"

    await chat_and_send(formatted_input, memory.working_messages, message.channel)


async def reflect(channel_id: discord.abc.Messageable) -> None:
    reflection_messages = [{"role": "system", "content": memory.PROMPT}]
    reflection_messages.append({"role": "system", "content": "You are in a reflection loop. Take this opportunity to reflect on what you currently know and understand to extrapolate any useful conclusions. You have access to all your tools, including your diary, so use it if you want to save anything from this context - messages will not persist after reflection ends."})

    formatted_input = f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] (System) Running recurring reflection"
    memory.dump_memory(reflection_messages, "data/reflection_messages.json")

    await chat_and_send(formatted_input, reflection_messages, channel_id)

# Auto loop tasks
@tasks.loop(minutes=120)
async def auto_loop() -> None:
    assert CHANNEL, "Channel uninitialized"
    await reflect(CHANNEL)

