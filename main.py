import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# load environment variables
load_dotenv('config/.env')

# setup intents (required for v2.0+)
intents = discord.Intents.default()

# using setattr to bypass strict PyCharm static attribute checking
setattr(intents, 'members', True)
setattr(intents, 'message_content', True)  # required to read command messages

client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

client.remove_command('help')


# asynchronously load cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


# main async function to start the bot
async def main():
    async with client:
        await load_extensions()

        # explicit null check to satisfy type checker
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("No token found. Please set DISCORD_TOKEN in your .env file.")

        await client.start(token)


if __name__ == '__main__':
    asyncio.run(main())