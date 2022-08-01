import imaplib, email, getpass
from email import policy
from email.header import decode_header
from pickle import decode_long
from re import L
from discord.errors import HTTPException
from discord.ext import commands, tasks
from discord.ext.commands import bot
import utilities
import assets
import discord
import json
import aiosqlite
import sqlite3

def log_counter():
    db = sqlite3.connect("./database.db")
    cur = db.cursor()
    cur.execute("SELECT COUNT (*) FROM mails")
    global new_case  
    result = cur.fetchone()
    new_case = result[0] + 1
    db.close()
    return new_case

class EmailListen(commands.Cog):
    """Email listener for incomming tickets or emails through the support email at strato."""
    def __init__(self, bot):
        self.bot = bot


    
    @tasks.loop(minutes=10)
    async def listener(self):
        db = await aiosqlite.connect("./database.db")
        embed = discord.Embed(title="Tickets", color = discord.Color.gold())
        channel = self.bot.get_channel(986977223326183444)
        imap_host = 'imap.strato.de'
        password = utilities.get_json(assets.config_file)
        mail = imaplib.IMAP4_SSL(imap_host, 993)
        rc, resp = mail.login(password['support-email'], password['support-password'])
        status, messages = mail.select("INBOX")
        N = 1
        messages = int(messages[0])
        for i in range(messages, messages-N, -1):
            resc, msg = mail.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding)
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("(Content-Disposistion)"))
                            try:
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                #print(body)
                                try:
                                    embed.add_field(name="From", value=From, inline=False)
                                    embed.add_field(name="Subject", value=subject)
                                    embed.add_field(name="Content", value =body, inline=False)
                                    await channel.send(embed=embed)
                                    print("[EMAIL] Embed sent \n")
                                    log_counter()
                                    await db.execute("INSERT OR IGNORE INTO mails VALUES (?, ?, ?, ?)", (new_case, From, subject, body))
                                    await db.commit()
                                    try:
                                        await db.close()
                                    except ValueError:
                                        pass
                                except HTTPException:
                                    try:
                                        #No body
                                        embed.add_field(name="From", value=From, inline=False)
                                        embed.add_field(name="Subject", value=subject)
                                        await channel.send(embed=embed)
                                        print("[EMAIL] Embed sent, email had no Content\n")
                                        log_counter()
                                        await db.execute("INSERT OR IGNORE INTO mails VALUES (?, ?, ?, ?)", (new_case, From, subject, "None"))
                                        await db.commit()
                                        try:
                                            await db.close()
                                        except ValueError:
                                            pass
                                    except HTTPException:
                                        #No subject
                                        try:
                                            embed.add_field(name="From", value=From, inline=False)
                                            embed.add_field(name="Content", value=body, inline=False)
                                            await channel.send(embed=embed)
                                            print("[EMAIL] Embed sent, email had no subject\n")
                                            log_counter()
                                            await db.execute("INSERT OR IGNORE INTO mails VALUES (?, ?, ?, ?)", (new_case, From, "None", body))
                                            await db.commit()
                                            try:
                                                await db.close()
                                            except ValueError:
                                                pass
                                        except HTTPException:
                                            pass


    @commands.Cog.listener()
    async def on_ready(self):
        db = await aiosqlite.connect("./database.db")
        await self.listener.start()



def setup(bot):
    bot.add_cog(EmailListen(bot))
