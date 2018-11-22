import discord
from discord.ext import commands
import aiosqlite
import paginator
import os

db_path = os.path.join(os.getcwd(), 'mathsbots.db')


class ShowDonations:
    def __init__(self, bot):
        self.bot = bot

    async def donationbytoday(self):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT donationsbytoday FROM season WHERE toggle = 1")
            dump = await c.fetchall()
        for donbytod in dump:
            return int(donbytod[0])

    @commands.command(name='don', aliases=['mydon'])
    async def mydon(self, ctx, userid: discord.Member=None):
        if not userid:
            userid = ctx.author.id
        else:
            userid = userid.id
        ign_embed = ''
        don_embed = ''
        dif_embed = ''
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT * FROM aw WHERE userid = ?', (userid,))
            dump = await c.fetchall()
            if len(dump) == 0:
                await ctx.send("Use `claim #PLAYERTAG` to claim an account: "
                               "either you or the person you pinged does not have any claimed accounts")
                return
            d = await db.execute("SELECT donations FROM aw WHERE userid = :id AND warning = 'Yes'", {'id':userid})
            numwarn = str(len(await d.fetchall()))
            for info in dump:
                ign = info[1]
                don = info[4] - info[3]
                dif = info[6]
                don_embed += (str(don) + '\n') + '\n'
                ign_embed += (str(ign) + '\n') + '\n'
                dif_embed += (str(dif) + '\n') + '\n'
        embed = discord.Embed(colour=8421504)
        embed.set_author(name='Donations required by today: '+ str(await self.donationbytoday()))
        embed.add_field(name='IGN', value=ign_embed)
        embed.add_field(name='Donations', value=don_embed)
        embed.add_field(name='Difference', value=dif_embed)
        embed.set_footer(text=f'Accounts not meeting requirements: {numwarn}')
        await ctx.send(embed=embed)

    @commands.command(name='awdon')
    async def awdon(self, ctx):
        try:
            ign_embed = ''
            don_embed = ''
            dif_embed = ''
            ping_text = ''
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT * FROM aw WHERE clan = :clan", {
                    'clan': 'Aussie Warriors',
                })
                dump = await c.fetchall()

                await db.close()
            for info in dump:
                ign = info[1]
                don = info[4] - info[3]
                dif = info[6]
                ping = info[7]
                ping_text += ping + ', '
                don_embed += (str(don) + '\n') + '\n'
                ign_embed += (str(ign) + '\n') + '\n'
                dif_embed += (str(dif) + '\n') + '\n'

            embed = discord.Embed(colour=8421504)
            embed.set_author(name='Donations required by today: ' + str(await self.donationbytoday()))
            embed.add_field(name='IGN', value=ign_embed)
            embed.add_field(name='Donations', value=don_embed)
            embed.add_field(name='Difference', value=dif_embed)
            embed.set_footer(text=f'To see averages use `avg`')
            embedhelp = discord.Embed(colour=9546812)
            embedhelp.set_footer(text='If this or any other messages have been sent in error, please ping mathsman#1208')
            await ctx.send(embed=embed)

        except discord.errors.HTTPException:
            await ctx.send('Hurray! Everybody has the required donations!')

    @commands.command(name='a4wdon')
    async def a4wdon(self, ctx):
        try:
            ign_embed = ''
            don_embed = ''
            dif_embed = ''
            ping_text = ''
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT * FROM aw WHERE clan = :clan", {
                    'clan': 'Aussies 4 War',
                })
                dump = await c.fetchall()
                for info in dump:
                    ign = info[1]
                    don = info[4] - info[3]
                    dif = info[6]
                    ping = info[7]
                    don_embed += (str(don) + '\n') + '\n'
                    ign_embed += (str(ign) + '\n') + '\n'
                    dif_embed += (str(dif) + '\n') + '\n'
                    ping_text += ping + ','

            embed = discord.Embed(colour=8421504)
            embed.set_author(name='Donations required by today: ' + str(await self.donationbytoday()))
            embed.add_field(name='IGN', value=ign_embed)
            embed.add_field(name='Donations', value=don_embed)
            embed.add_field(name='Difference', value=dif_embed)
            embed.set_footer(text=f'To see averages use `avg`')
            embedhelp = discord.Embed(colour=9546812)
            embedhelp.set_footer(text='If this or any other messages have been sent in error, please ping mathsman#1208')
            await ctx.send(embed=embed)

        except discord.errors.HTTPException:
            await ctx.send('Hurray! Everybody has the required donations!')

    @commands.command(name='avg')
    async def avg(self, ctx, userid:discord.Member=None):
        if userid:
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT averagedonations, userid FROM averages WHERE userid = :id", {'id':userid.id})
                dump = await c.fetchall()
        else:
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT averagedonations, userid FROM averages WHERE warning = 'Yes'")
                dump = await c.fetchall()
        send1 = []
        for info in dump:
            avgdon = info[0]
            id = f'<@{info[1]}>'
            line = ''
            line += '{:>0} Avg Don Dif:'.format(id)
            line += '{:>12}'.format(avgdon)
            send1.append(line)
        pages = paginator.EmbedPag(ctx, entries=send1, per_page=30, message=ctx.message)
        await pages.paginate(start_page=1)

    @commands.command(name='myavg')
    async def myavg(self, ctx):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT averagedonations, userid FROM averages WHERE userid = :id", {'id':ctx.author.id})
            dump = await c.fetchall()
        id_text = ''
        avg_text = ''
        for info in dump:
            avgdon = info[0]
            id = info[1]
            avg_text += str(avgdon) + '\n'
            id_text += f'<@{id}>' + '\n'
        e = discord.Embed(colour=8421504)
        e.add_field(name="Discord Name", value=id_text)
        e.add_field(name="Average Donations", value=avg_text)
        try:
            await ctx.send(embed=e)
        except discord.HTTPException:
            await ctx.send("No accounts have warnings! Great job :tada:")



def setup(bot):
    bot.add_cog(ShowDonations(bot))
