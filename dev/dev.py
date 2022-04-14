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
            await db_conn.execute("CREATE TABLE IF NOT EXIST moderationlogs(logid INTEGER PRIMARY KEY, guildid int, moderationlogtype int, userid int, moduserid int)")



    






def setup(bot):
    bot.add_cog(dev(bot))
