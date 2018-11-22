import discord
from discord.ext import commands
import aiosqlite
import os

db_path = os.path.join(os.getcwd(), 'mathsbots.db')


class ClaimExemptCommands:
    def __init__(self, bot):
        self.bot = bot

    async def donationbytoday(self):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT donationsbytoday FROM season WHERE toggle = 1")
            dump = await c.fetchall()
        for donbytod in dump:
            return int(donbytod[0])

    @commands.command(name='claim')
    async def claim(self, ctx, tag: str=None, userid: discord.Member = None):
        if not tag:
            await ctx.send("Please include a player tag!")
            return
        if not userid:
            userid = ctx.author
        players = self.bot.coc.players('{}'.format(tag)).get()
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT * FROM aw WHERE tag = ? AND userid = ?', (tag, userid.id))
            result = await c.fetchall()
            await db.close()
        if len(result) == 0:
            try:
                ignname = players['name']
                player = self.bot.coc.players('{}'.format(tag)).get()
                ign = player['name']
                for achievement in player['achievements']:
                    if achievement['name'] == 'Friend in Need':
                        don = achievement['value']
                rec = don
                dif = str(await self.donationbytoday())
                warn = 'No'
                ping = userid.mention
                try:
                    clan = player['clan']['name']
                except KeyError:
                    clan = ''
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        'INSERT INTO aw VALUES (:tag, :ign, :userid, :don, :rec, :warn, :dif, :ping, :clan, :exempt)', {
                            'tag': tag,
                            'ign': ign,
                            'userid': userid.id,
                            'don': don,
                            'rec': rec,
                            'warn': warn,
                            'dif': dif,
                            'ping': ping,
                            'clan': clan,
                            'exempt': 'No',
                        })
                    await db.close()
                await ctx.send(f'You have claimed {ignname}')
            except KeyError:
                await ctx.send(f'The player tag of: {tag} was not found. Please ensure the player tag is correct and try again. ')
        else:
            try:
                ign = players['name']
                await ctx.send(f'You have already claimed {ign}. To see your claims, type `myclaims`')
            except KeyError:
                await ctx.send(f'The player tag of: {tag} was not found. Please ensure the player tag is correct and try again. ')


    @commands.command(name='del')
    async def delclaim(self, ctx, tag: str=None):
        if not tag:
            await ctx.send('You need to include a player tag to delete!')
            return
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT * FROM aw WHERE tag = ?', (tag,))
            result = await c.fetchall()
            await db.close()

        if len(result) == 0:
            await ctx.send(f'It seems like an account with that tag has not been claimed! Please type `claim {tag}` to claim your account!')
        else:
            async with aiosqlite.connect(db_path) as db:
                await db.execute("DELETE FROM aw WHERE tag='{}'".format(tag))
                await db.close()
            await ctx.send('Sucessfully deleted. You can check your claims by typing `myclaims`.')

    @commands.command(name='exempt')
    async def exempt(self, ctx, tag:str=None):
        if not tag:
            await ctx.send("Please include a playertag. To find these type `gc`")
            return
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT * FROM aw WHERE tag = ?', (tag,))
            result = await c.fetchall()
            db.close()
        if len(result) == 0:
            await ctx.send(f'No claimed account was found with tag: {tag}! Please type `claim {tag}` to claim your account and try again.')
        else:
            async with aiosqlite.connect(db_path) as db:
                await db.execute("UPDATE aw SET exempt='Yes' WHERE tag = ?", (tag,))
                players = self.bot.coc.players('{}'.format(tag)).get()
                name = players['name']
                await ctx.send(f'{name} has been added to the `exemptlist`.')


    @commands.command(name='delexempt')
    async def delexempt(self, ctx, tag:str=None):
        if not tag:
            await ctx.send("Please include a player tag")
            return
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT * FROM aw WHERE tag = ?', (tag,))
            result = await c.fetchall()
            await db.close()
        if len(result) == 0:
            await ctx.send(f'No claimed account was found with tag: {tag}! Please type `claim {tag}` to claim your account.')
        else:
            async with aiosqlite.connect(db_path) as db:
                await db.execute("UPDATE aw SET exempt='No' WHERE tag = ?", (tag,))
                await db.close()
            players = self.bot.coc.players('{}'.format(tag)).get()
            name = players['name']
            await ctx.send(f'{name} has been removed from the `exemptlist`.')



    @commands.command(name='exemptlist')
    async def exemptlist(self, ctx):
        try:
            name_text = ''
            ping_text = ''
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT * FROM aw WHERE exempt = 'Yes'")
                dump = await c.fetchall()
            for info in dump:
                name = info[1]
                ping = info[7]
                name_text += str(name) + '\n'
                ping_text += str(ping) + '\n'
            embed = discord.Embed(colour=8421504)
            embed.set_author(name='Exempt from Donation Tracker: ')
            embed.add_field(name='IGN', value=name_text)
            embed.add_field(name='Discord Name', value=ping_text)
            embed.set_footer(text=f'Total number of exempt accounts: {str(len(dump))}')
            await ctx.send(embed=embed)
        except discord.errors.HTTPException:
            await ctx.send('No accounts on the exempt list!')


def setup(bot):
    bot.add_cog(ClaimExemptCommands(bot))