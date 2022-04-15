import asyncio
import discord
from discord.ext import commands
import aiosqlite
db = "./database.db"
task_list = "Running task {}/3"

class dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="dbsetup")
    @commands.is_owner()
    async def dbsetup(self, ctx):
        db_conn = await aiosqlite.connect(db)
        msg = await ctx.send(task_list.format("1"))
        try:
            await db_conn.execute("CREATE TABLE IF NOT EXISTS moderationlogs(logid INTEGER PRIMARY KEY, guildid int, moderationlogtype int, userid int, moduserid int, content varchar, duration int, raw_time text)")
            await db_conn.commit()
        except Exception as e:
            return await msg.edit(content=f"Failed to complete task 1/3 Because of: `{e}`")
        await asyncio.sleep(2)
        await msg.edit(content = task_list.format("2"))
        try:
            await db_conn.execute("CREATE TABLE IF NOT EXISTS logtypes (ID INTEGER PRIMARY KEY, type TEXT)")
            await db_conn.commit()
        except Exception as e:
            return await msg.edit(content = f"Failed to complete task 2/3 because of: `{e}`")
        await asyncio.sleep(2)
        await msg.edit(content = task_list.format("3"))
        try:
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (1, "warn",))
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (2, "mute",))
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (3, "unmute",))
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (4, "kick",))
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (5, "softban",))
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (6, "ban",))
            await db_conn.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (7, "unban",))
            await db_conn.commit()
        except Exception as e:
            return await msg.edit(content = f"Failed to complete task 3/3 because of: `{e}`")
        await asyncio.sleep(2)
        await msg.edit(content = "Done")

        try:
            await db_conn.close()
        except ValueError:
            pass
        except Exception as e:
            return await msg.edit(content=f"Failed to close the database because of {e}")

    @commands.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, *, extension, hidden=True):
        try:
            await self.bot.load_extension(extension)
        except Exception as e:
            return await ctx.send(f"{type(e).__name__} - {e}")
    
    @commands.command(name="unload")
    @commands.is_owner()
    async def unload (self, ctx, module):
        try:
            await self.bot.unload_extension(module)
        except Exception as e:
            return await ctx.send(f"{type(e).__name__} - {e}")
    
    @commands.command(name="reload")
    @commands.is_owner()
    async def _reload(self, ctx, module):
        try:
            await self.bot.unload_extension(module)
            await self.bot.load_extension(module)
        except Exception as e:
            return await ctx.send(f"{type(e).__name__} - {e}")


    






def setup(bot):
    bot.add_cog(dev(bot))
