import json
import aiosqlite
from aiosqlite import DatabaseError
import imaplib, email, getpass
from email import policy
import utilities
import assets
import discord

def get_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=4)


async def get_prefix(_bot, message):
    db = await aiosqlite.connect("./database.db")
    try:
        async with db.execute("SELECT prefix FROM guilds WHERE guildid = ?", (message.guild.id,)) as cursor:
            async for entry in cursor:
                prefix = entry
                return prefix
        await db.close()
    except ValueError:
        pass
    except Exception as e:
        return print(e)


