import argparse
from asyncio.runners import run
import discord
from discord.ext import commands, tasks
import json
from datetime import datetime
from argparse import ArgumentParser
from discord.ext.commands.core import command
import assets
from itertools import cycle
import tqdm
import utilities
start_date = datetime.utcnow()
start_date_pretty = start_date.strftime("%d/%m/%Y %H:%M:%S")

dev_mode = False
parser = argparse.ArgumentParser(description="Run the bot in dev mode.")
parser.add_argument("--dev", action="store_true")
args = parser.parse_args()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True

if args.dev:
    dev_mode = True

print(f"Bot started on {start_date_pretty}\n")

nerd = commands.Bot(command_prefix="dd!", case_insensitve = True, intents = intents)
print("Removing help, ping command")
nerd.remove_command("help")
nerd.remove_command("ping")

print("Setting status\n")
status = cycle(assets.status_cycle)

if __name__ == "__main__":
    for extension in assets.extensions:
        nerd.load_extension(extension)


@tasks.loop(minutes=3)
async def change_status():
    global status
    status = cycle(assets.status_cycle)
    await nerd.change_presence(activity=discord.Game(next(status)))

@nerd.event
async def on_ready():
    global status
    change_status.start()
    await nerd.change_presence(activity=discord.Game(next(status)))


token = utilities.get_json(assets.config_file)

if dev_mode:
    run_token = token["dev_token"]
    nerd.run(run_token)
else:
    run_token = token["token"]
    nerd.run(run_token)


