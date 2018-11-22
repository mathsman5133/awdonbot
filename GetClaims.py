import discord
from discord.ext import commands
import aiosqlite
import os


db_path = os.path.join(os.getcwd(), 'mathsbots.db')


class GetClaims:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gc')
    async def gc(self, ctx, userid: discord.Member=None):
        if not userid:
            name = ctx.author.display_name
            userid = ctx.author.id
        else:
            name = userid.display_name
            userid = userid.id
        ign_text = ''
        tag_text = ''

        try:
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT * FROM aw WHERE userid='{}'".format(userid))
                dump = await c.fetchall()
                for info in dump:
                    ign = info[1]
                    tag = info[0]
                    ign_text += ign + '\n'
                    tag_text += tag + '\n'
                numclaims = await db.execute("SELECT ign FROM aw WHERE userid=:userid", {'userid':userid})
                numclaims = str(len(await numclaims.fetchall()))
                await db.close()
            embed = discord.Embed(colour=10532080)
            embed.set_author(name='Claimed Accounts:')
            embed.add_field(name='IGN', value=ign_text)
            embed.add_field(name='Tag', value=tag_text)
            embed.set_footer(text=f'Number of claimed accounts: {numclaims}')
            await ctx.send(embed=embed)
        except discord.errors.HTTPException:
            await ctx.send(f"It seems {name} doesn't have any claims! Type `claim #PLAYERTAG` to claim an account.")


    @commands.command(name='a4wgm')
    async def a4wgm(self, ctx):
        claimedigntext = ''
        claimedtagtext = ''
        claimedpingtext = ''
        unclaimedigntext = ''
        unclaimedtagtext = ''
        aw = self.bot.coc.clans('#808URP9P').get()
        members = aw['memberList']
        for member in members:
            tag = member['tag']
            name = member['name']
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT ping FROM aw WHERE tag = '{}'".format(tag))
                dump = await c.fetchall()
            if len(dump) != 0:
                for acct in dump:
                    claimedigntext += name + '\n'
                    claimedtagtext += tag + '\n'
                    claimedpingtext += acct[0] + '\n'
            else:
                unclaimedigntext += name + '\n'
                unclaimedtagtext += tag + '\n'


        embed = discord.Embed(colour=0x00FF00)
        embed.set_author(name="Aussies 4 War Base Claims")
        embed.add_field(name="IGN", value=claimedigntext)
        embed.add_field(name="Discord Name", value=claimedpingtext)
        embed.add_field(name="No Claims:", value=unclaimedigntext, inline=False)
        embed.add_field(name="Tag", value=unclaimedtagtext)
        await ctx.send(embed=embed)


    @commands.command(name='awgm')
    async def awgm(self, ctx):
        claimedigntext = ''
        claimedtagtext = ''
        claimedpingtext = ''
        unclaimedigntext = ''
        unclaimedtagtext = ''
        aw = self.bot.coc.clans('#P0LYJC8C').get()
        members = aw['memberList']
        for member in members:
            tag = member['tag']
            name = member['name']
            async with aiosqlite.connect(db_path) as db:
                c = await db.execute("SELECT ping FROM aw WHERE tag = '{}'".format(tag))
                dump = await c.fetchall()
            if len(dump) != 0:
                for acct in dump:
                    claimedigntext += name + '\n'
                    claimedtagtext += tag + '\n'
                    claimedpingtext += acct[0] + '\n'
            else:
                unclaimedigntext += name + '\n'
                unclaimedtagtext += tag + '\n'
        embed = discord.Embed(colour=0x00FF00)
        embed.set_author(name="Aussie Warriors Base Claims")
        embed.add_field(name="IGN", value=claimedigntext)
        embed.add_field(name="Discord Name", value=claimedpingtext)
        embed.add_field(name="No Claims:", value=unclaimedigntext, inline=False)
        embed.add_field(name="Tag", value=unclaimedtagtext)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(GetClaims(bot))