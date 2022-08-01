import argparse
from sqlite3.dbapi2 import IntegrityError
import discord
from discord.ext import commands, tasks
import aiosqlite
from datetime import datetime
from discord.ext.commands.core import command
import assets
from itertools import cycle
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
print("-" * 100)
print("DDIT's Guard developed by Senpai_Desi#4108")
print("-" *100 ) 
print(f"[INFO] Bot started on {start_date_pretty}")

bot = commands.Bot(command_prefix=utilities.get_prefix, case_insensitve = True, intents = intents)
print("[BOT SETUP] Removing help, ping command.")
bot.remove_command("help")
bot.remove_command("ping")

print("[BOT SETUP] Setting status.\n")
status = cycle(assets.status_cycle)

if __name__ == "__main__":
    for extension in assets.extensions:
        bot.load_extension(extension)


@tasks.loop(minutes=3)
async def change_status():
    global status
    status = cycle(assets.status_cycle)
    await bot.change_presence(activity=discord.Game(next(status)))

@bot.event
async def on_guild_join(_guild):
    db = await aiosqlite.connect("database.db")
    for guild in bot.guilds:
        try:
            await db.execute("CREATE TABLE IF NOT EXISTS guilds (guildid INTEGER UNIQUE, prefix TEXT)")
            await db.commit()
            await db.execute(f"INSERT INTO guilds VALUES ({_guild.id}, 'dd!')")
            await db.commit()
            print(f"[GUILD JOIN] {_guild.id} got added with basic prefix of (dd!).")
        except IntegrityError:
            print(f"[GUILD JOIN] {_guild.id} Already exists.")
        except ValueError:
            pass
        try:
            await db.close()
        except ValueError:
            pass


@bot.event
async def on_ready():
    db = await aiosqlite.connect("database.db")
    global status
    change_status.start()
    await bot.change_presence(activity=discord.Game(next(status)))
    for guild in bot.guilds:
        await on_guild_join(guild)
    print("[INFO] Bot is online\n")


@bot.command(name="prefix")
@commands.has_permissions(ban_members=True)
async def setprefix(ctx, _prefix = None):
    """Change your prefix. Format dd!prefix <New prefix>"""
    db = await aiosqlite.connect("database.db")
    if _prefix is not None:
        await db.execute(f"DELETE FROM guilds WHERE guildid = {ctx.guild.id} ")
        await db.commit()
        await db.execute(f"INSERT INTO guilds (guildid, prefix) VALUES (?, ?)", (ctx.guild.id, str(_prefix),))
        await db.commit()
        await ctx.send(f"Done! Your new prefix is {_prefix}")
        print(f"[GUILD UPDATE] {ctx.guild.id} changed their prefix to {_prefix}\n")
        try:
            await db.close()
        except ValueError:
            pass
    else:
        return await ctx.send(f"Your current prefix is {ctx.prefix}.")


token = utilities.get_json(assets.config_file)

if dev_mode:
    run_token = token["dev_token"]
    bot.run(run_token)
else:
    run_token = token["token"]
    bot.run(run_token)


