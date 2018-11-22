from discord.ext import commands
import aiosqlite
import datetime
import os

db_path = os.path.join(os.getcwd(), 'mathsbots.db')


class UpdateCommands:
    def __init__(self, bot):
        self.bot = bot

    async def new_avg(self, userid):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT difference FROM aw WHERE userid = :id", {'id':userid})
            dump = await c.fetchall()
            await db.close()
        total_difference = 0
        for acctdon in dump:
            total_difference += int(acctdon[0])
        avg = -(int(total_difference / len(dump)))
        if avg >= await self.donationbytoday():
            warn = 'No'
        else:
            warn = 'Yes'
        async with aiosqlite.connect(db_path) as db:
            await db.execute("INSERT INTO averages VALUES(:userid,:avg,:warn)", {'avg':avg, 'warn':warn, 'userid':userid})
            await db.commit()
            await db.close()

    async def donationbytoday(self):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT donationsbytoday FROM season WHERE toggle = 1")
            dump = await c.fetchall()
        for donbytod in dump:
            return int(donbytod[0])

    async def upd_donationsbytoday(self):
        dayofyear = datetime.datetime.utcnow().strftime('%j')
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT startdate FROM season WHERE toggle = 1")
            dump = await c.fetchall()
            await db.close()
        for startdate in dump:
            datedif = int(dayofyear) - startdate[0]
        donreq = datedif * 13.33
        async with aiosqlite.connect(db_path) as db:
            await db.execute("UPDATE season SET donationsbytoday = :donreq WHERE toggle = 1", {'donreq':donreq})
            await db.commit()
            await db.close()

    @commands.command()
    async def udd(self, ctx):
        await self.upd_donationsbytoday()
        print('done')

    async def new_month(self):
        dayofyear = datetime.datetime.now().strftime('%j')
        async with aiosqlite.connect(db_path) as db:
            await db.execute("INSERT INTO season VALUES (:toggle, :donbytod, :startdate)", {'toggle':1, 'donbytod':13.3, 'startdate':dayofyear})
            await db.commit()
            await db.close()
            print('done')

    async def dlstartingdonations(self, tag):
        memberinfo = self.bot.coc.players(tag).get()
        achievements = memberinfo['achievements']
        for achievement in achievements:
            if achievement['name'] == 'Friend in Need':
                troopsdon = achievement['value']
                async with aiosqlite.connect(db_path) as db:
                    await db.execute("UPDATE aw SET donations=:don WHERE tag = :tag", {'don':troopsdon, 'tag':tag})
                    await db.close()

    async def updclandb(self, don, dif, warn, clan, tag):
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                'UPDATE aw \n'
                'SET received=:rec,\n'
                'difference=:dif,\n'
                'warning=:warn,\n'
                'clan=:clan\n'
                'WHERE tag=:tag',
                {
                    'rec': don,
                    'dif': dif,
                    'warn': warn,
                    'clan': clan,
                    'tag': tag,
                })
            await db.close()

    async def my_upd(self, userid):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT tag FROM aw WHERE userid = ?', (userid,))
            tags = await c.fetchall()
            for tag1 in tags:
                tag = tag1[0]
                player = self.bot.coc.players('{}'.format(tag)).get()
                for achievement in player['achievements']:
                    if achievement['name'] == 'Friend in Need':
                        don = achievement['value']
                c = await db.execute("SELECT donations FROM aw WHERE tag = :tag", {'tag': tag})
                dump = await c.fetchall()
                for donations in dump:
                    starting_donations = donations[0]
                achdif = int(don) - int(starting_donations)
                dif = str(await self.donationbytoday() - achdif)
                if achdif <= await self.donationbytoday():
                    warn = 'Yes'
                if achdif >= await self.donationbytoday():
                    warn = 'No'
                try:
                    clan = player['clan']['name']
                except KeyError:
                    clan = ''
                await self.updclandb(don, dif, warn, clan, tag)
                await db.close()

    async def update(self):
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute('SELECT tag FROM aw')
            tags = await c.fetchall()
            for tag1 in tags:
                tag = tag1[0]
                player = self.bot.coc.players('{}'.format(tag)).get()
                for achievement in player['achievements']:
                    if achievement['name'] == 'Friend in Need':
                        don = achievement['value']
                c = await db.execute("SELECT donations FROM aw WHERE tag = :tag", {'tag': tag})
                dump = await c.fetchall()
                for donations in dump:
                    starting_donations = donations[0]
                achdif = int(don) - int(starting_donations)
                dif = str(await self.donationbytoday() - achdif)
                try:
                    clan = '{}'.format(player['clan']['name'])
                except KeyError:
                    clan = ''
                if achdif <= await self.donationbytoday():
                    warn = 'Yes'
                if achdif >= await self.donationbytoday():
                    warn = 'No'
                await self.updclandb(don, dif, warn, clan, tag)
                await self.refresh_avg()

    async def refresh_avg(self):
        async with aiosqlite.connect(db_path) as db:
            await db.execute('drop table averages')
            await db.execute('CREATE TABLE `averages` '
                             '( `userid` INTEGER, `averagedonations` INTEGER, `warning` TEXT )')
            await db.commit()
            c = await db.execute("select userid from aw where clan = 'Aussies 4 War' or clan = 'Aussie Warriors'")
            dump = list(set(await c.fetchall()))
            await db.close()
        for a in dump:
            await self.new_avg(a[0])

    @commands.command(name='refavg')
    async def _refresh_avg(self, ctx):
        await self.refresh_avg()
        await ctx.send('done')

    @commands.command(name='upd')
    async def _update(self, ctx):
        await ctx.send("This will take a while. Please be patient")
        await self.update()
        await self.upd_donationsbytoday()
        await ctx.send(
            "All players' donations have been updated. "
            "You can now type `mydon`, `awdon` or `a4wdon` to see respective donations."
        )

    @commands.command(name='myupd')
    async def myupd(self, ctx):
        await ctx.send("This will take a while. Please be patient")
        userid = ctx.author.id
        await self.my_upd(userid)
        await ctx.send(
            'Updated donations for your claimed accounts. '
            'To see these type `myclaims`, and to find your donations type `mydon`'
        )

    @commands.command(name='manreset')
    async def man_reset(self, ctx):
        await ctx.send("This may take a minute")
        async with aiosqlite.connect(db_path) as db:
            await db.execute("UPDATE season SET toggle = 0")
            await db.commit()
            c = await db.execute("SELECT tag FROM aw")
            dump = await c.fetchall()
        await self.new_month()
        for tag in dump:
            await self.dlstartingdonations(tag[0])
        await self.refresh_avg()
        await ctx.send("Monthly donation dump completed")


def setup(bot):
    bot.add_cog(UpdateCommands(bot))
