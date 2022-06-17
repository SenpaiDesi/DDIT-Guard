import asyncio
from multiprocessing.sharedctypes import Value
import discord
from discord.ext import commands
import aiosqlite
import aiosqlite
import sqlite3
import re
from discord.ext.commands.converter import EmojiConverter
from discord.ext.commands.errors import MissingPermissions








time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

def log_counter():
    db = sqlite3.connect("./database.db")
    cur = db.cursor()
    cur.execute("SELECT COUNT (*) FROM moderationLogs")
    global new_case  
    result = cur.fetchone()
    new_case = result[0] + 1
    return new_case


def log_converter(type):
    global newtype
    if type == 1:
        newtype = "warn"
        return newtype
    elif type == 2 :
        newtype = "mute"
        return newtype
    elif type == 3:
        newtype = "unmute"
        return newtype
    elif type == 4 :
        newtype = "kick"
        return newtype
    elif type == 5:
        newtype = "softban"
        return newtype
    elif type == 6:
        newtype = "ban"
        return newtype
    elif type == 7:
        newtype = "unban"
        return newtype


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        global args
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class Moderation(commands.Cog):
    """Moderation commands for people who do not listen and other utils."""
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name="addrole")
    @commands.has_permissions(ban_members = True)
    async def addrole(self, ctx, role : discord.Role = None, member : discord.Member = None):
        """Adds a role to a user, Format addrole @role @user """
        msg = await ctx.send("Role process")
        if role is not None:
            if member is not None:
                if member.top_role >= ctx.author.top_role:
                    await msg.edit(content = f"Failed to add a role to {member.mention} Because their role is higher then yours!")
                else:
                    await member.add_roles(role)
                    await msg.edit(content = f"✅ Added {role.mention} to {member.mention}")
            else:
                await msg.edit(content = f"❌ Could not add {role.name} to that user because I could not find that member or it does not exit.")
        else:
            await msg.edit(content = "❌Could not add that role to {member.mention} because I could not find {role}!")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=  True)
    async def ban(self, ctx, member : discord.Member = None, *, reason = None):
        """Bans an user from the server. Format: ban @user reason"""
        db = await aiosqlite.connect("./database.db")
        embed = discord.Embed(title="Ban", description="Ban a member", color = discord.Color.red())
        userembed = discord.Embed(title = "Banned", description="You got banned", color = discord.Color.random() )
        log_counter()
        if member is not None:
            if member.top_role >= ctx.author.top_role:
                embed.description(description = f"Can not ban {member.mention} because his roles are higher then you.")
            else:
                await member.ban(reason=reason)
                await db.execute("INSERT OR IGNORE INTO moderationLogs VALUES (?, ?, ?, ?, ?, ?, ?)", (new_case,ctx.guild.id, 6, member.id, ctx.author.id, reason, "0"))
                try:
                    userembed.add_field(name = f"You got banned in **{ctx.guild.name}**", value=" for: \n{reason}", inline=False)
                    await member.send(embed = userembed)
                    embed.add_field(name = f"✅Banned {member.name}#{member.discriminator}", value= " for\n**{reason}**", inline=False)
                except discord.errors.Forbidden:
                    embed.add_field(name = f"✅Logged ban for {member.name}#{member.discriminator}.", value=" I could not dm them.", inline=False)
        else:
            embed.add_field(name = "Error", value="I could not ban because that user is not in this server or not found.", inline=False)
        await ctx.send(embed = embed)
        try:
            await db.close()
        except ValueError:
            pass
    @commands.command(name = 'kick')
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member = None, *, reason = None):
        """Kicks  an  user, format: kick @user reason."""
        log_counter()
        db  = await aiosqlite.connect("./database.db")
        userembed = discord.Embed(title = "Kicked", color = discord.Color.orange())
        embed = discord.Embed(title = "Kicked user", color = discord.Color.green())
        if member is not None:
            if member.top_role >= ctx.author.top_role:
                embed.add_field(name="Error", value="Your role is lower then the target's role so I am unable to kick him")
            else:
                try:
                    member.kick(reason = reason)
                    await db.execute("INSERT OR IGNORE INTO moderationLogs VALUES (?, ?, ?, ?, ?, ?, ?)", (new_case, ctx.guild.id, 4, member.id, ctx.author.id, reason,  "0",))
                    await db.commit()
                    try:
                        await db.close()
                    except ValueError:
                        pass
                    userembed.add_field(name = "Kicked", value = f"You got kicked in {ctx.guild.name} for\n{reason}", inline=False)
                    embed.add_field(name=f"✅ Kicked {member.name}#{member.discriminator}", value=reason, inline=False)
                except discord.errors.Forbidden:
                    embed.add_field(f"Logged kick for {member.name}#{member.discriminator}. I could not dm them")
        else:
            embed.add_field(name="The user provided could not be found or does not exist.")
        await ctx.send(embed = embed)


    @commands.command(name="warn")
    @commands.has_permissions(kick_members = True)
    async def warn(self, ctx, member : discord.Member = None, *, reason = None):
        """Warns an user. Format: warn @user reason """
        log_counter()
        db = await aiosqlite.connect("./database.db")
        embed = discord.Embed(title = "Warning", color = discord.Color.gold())
        userembed = discord.Embed(title = "Warning received", color = discord.Color.red())
        try:
            if member is not None:
                    try:
                        await db.execute("INSERT OR IGNORE INTO moderationLogs VALUES (?, ?, ?, ?, ?, ?, ?)", (new_case, ctx.guild.id, 1, member.id, ctx.author.id, reason, "0", ))
                        await db.commit()
                        await db.close()
                    except ValueError:
                        pass
                    try:
                        userembed.add_field(name=f"Warned in {ctx.guild.name}", value=reason, inline=False)
                        embed.add_field(name="Success", value=f"Warned {member.name}#{member.discriminator} for {reason}")
                    except discord.errors.Forbidden:
                        embed.add_field("Success", value=f"Logged warning for {member.name}#{member.discriminator} because I could not dm them.")
            else:
                await embed.add_field(name="Failed", value="Failed to warn because this user does not exist or I could not find them.")
        except MissingPermissions:
            embed.add_field(name = "Failed to warn", value="You do not have the permissions to warn someone (kick_members)")
        await ctx.send(embed = embed)

    @commands.command(name="modlogs")
    @commands.has_permissions(kick_members = True)
    async def modlogs (self, ctx, member : discord.Member = None):
        db = await aiosqlite.connect("./database.db")
        embed =discord.Embed(title = f"Showing logs for {member.id}", description="___ ___", color = discord.Color.dark_blue())
        msg = await ctx.send(embed = embed)
        try:
            async with db.execute('SELECT logid, moderationLogTypes, moduserid, content, duration FROM moderationLogs WHERE guildid = ? AND userid = ?', (ctx.guild.id, member.id)) as cursor:
                async for entry in cursor:
                    logid, moderationLogTypes, moduserid, content, duration  = entry
                    Moderator = self.bot.get_user(moduserid)
                    type = log_converter(moderationLogTypes)
                    if duration == "0":
                        embed.add_field(name=f"**Case {logid}**", value= f"**User:**{member.name}#{member.discriminator}\n**Type:**{type}\n**Admin:**{Moderator.name}#{Moderator.discriminator}\n**Reason:**{content}", inline=False)
                    else:
                        embed.add_field(name=f"**Case {logid}**", value= f"**User:**{member.name}#{member.discriminator}\n**Type:**{type}\n**Admin:**{Moderator.name}#{Moderator.discriminator}\n**Reason:**{content}\n**Duration:**{duration}", inline=False)
        except Exception as e:
            return await ctx.send(e)
        await msg.edit(embed = embed)
        await asyncio.sleep(2)
        await db.close()
    



    @commands.command(name='mute')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member : discord.Member, time : TimeConverter= None, *, reason = None):
        """Mute an  user. Format @user time(optional, 1h, 1d etc) Reason for mute"""
        db = await aiosqlite.connect("./database.db")
        role =  discord.utils.get(ctx.guild.roles, name="Muted")

        
        role_to_remove = []
        log_counter()
        if not role:
            await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=False)
        try:
            if member is not None:
                if time is not None:
                    await member.edit(roles = [])
                    await member.add_roles(role)
                    await db.execute("INSERT INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES(?, ?, ?, ?, ?, ?, ?)",(new_case, ctx.guild.id, 2, member.id, ctx.author.id, reason, args))
                    await db.commit()
                    await asyncio.sleep(2)
                    await db.close()
                    embed = discord.Embed(title="Muted", description=f"Muted {member.name}#{member.discriminator}", color  = discord.Color.green())
                    try:
                        await member.send(f"You got muted in **{ctx.guild.name}** for {reason} and lasts {args}.")
                    except discord.errors.Forbidden:
                        return await ctx.send(f"Logged mute, could not dm <@{member.id}>")
                    await asyncio.sleep(time)
                    await member.remove_roles(role)
                else:
                    await member.edit(roles = [])
                    await member.add_roles(role)
                    await db.execute("INSERT INTO moderationLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES(?, ?, ?, ?, ?, ?, ?)",(new_case, ctx.guild.id, 2, member.id, ctx.author.id, reason, "0"))
                    await db.commit()
                    await asyncio.sleep(2)
                    await db.close()
                    embed = discord.Embed(title="Muted", description=f"Muted {member.name}#{member.discriminator}", color  = discord.Color.green())
                    try:
                        await member.send(f"You got muted in **{ctx.guild.name}** for {reason} and is permanent.")
                    except discord.errors.Forbidden:
                        return await ctx.send(f"Logged mute, could not dm <@{member.id}>")
            else:
                if member == ctx.author:
                    return await ctx.send("You can not mute yourself")
                elif member == self.bot.user:
                    return await ctx.send("Sorry You can not mute me")
        except discord.errors.Forbidden:
            return await ctx.send("You can't mute this user.")

    @commands.command(name='unmute')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member : discord.Member, *, reason = None):
        db = await aiosqlite.connect("./database.db")
        new_case()
        if member is not None:
            embed = discord.Embed(name="Unmute", color = discord.Color.dark_blue())
            try:
                for role in member.roles:
                    if role.name == "Muted":
                        await member.edit(roles = [])
            except Exception as e: 
                embed.add_field(name="Error", value=f"Failed to unmute {member.name}#{member.discriminator} {e}")
            embed.add_field(name="Unmuted", value=f"Unmuted {member.name}#{member.discriminator}")
            try:
                await db.execute("INSERT OR IGNORE INTO moderationgLogs (logid, guildid, moderationLogTypes, userid, moduserid, content, duration) VALUES(?, ?, ?, ?, ?, ?, ?)",(new_case, ctx.guild.id, 3, member.id, ctx.author.id, reason, ))
                await db.commit()
                await db.close()
            except ValueError:
                pass
            except Exception as e:
                embed.add_field(name='Error!', value=f"Failed to unmute because of {e}")
        await ctx.send(embed=embed)








def setup(bot):
    bot.add_cog(Moderation(bot))