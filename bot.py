from coc import ClashOfClans
import discord
from discord.ext import commands
import logging
import sys
import datetime
import time
import traceback
import json
import os
import functools

json_location = os.path.join(os.getcwd(), 'creds.json')
db_path = os.path.join(os.getcwd(), 'mathsbots.db')

errorhookid = 510761692045770767
errorhooktoken = "bGNHEoq6HEvZN4oHezkZ9bhpvKoHOQp0CCBgZjq990Qu3UTQfd_JgCFtdceFZNS_TInf"
errorhook = discord.Webhook.partial(id=errorhookid, token=errorhooktoken, adapter=discord.RequestsWebhookAdapter())

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
#logger.addHandler(logging.StreamHandler(sys.stdout))
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)


bot = commands.Bot(command_prefix='', case_insensitive=True)
bot.remove_command('help')

initial_extensions = ['ClaimExemptCommands', 'UpdateCommands', 'ShowDonations', 'GetClaims']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(e)


class Misc:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        # we dont want logs for this stuff which isnt our problem
        ignored = (commands.NoPrivateMessage, commands.DisabledCommand, commands.CheckFailure,
                   commands.CommandNotFound, commands.UserInputError, discord.Forbidden)
        error = getattr(error, 'original', error)
        # filter errors we dont want
        if isinstance(error, ignored):
            return
        # send error to log channel
        e = discord.Embed(title='Command Error', colour=0xcc3366)
        e.add_field(name='Name', value=ctx.command.qualified_name)
        e.add_field(name='Author', value=f'{ctx.author} (ID: {ctx.author.id})')

        fmt = f'Channel: {ctx.channel} (ID: {ctx.channel.id})'
        if ctx.guild:
            fmt = f'{fmt}\nGuild: {ctx.guild} (ID: {ctx.guild.id})'

        e.add_field(name='Location', value=fmt, inline=False)
        # format legible traceback
        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
        e.description = f'```py\n{exc}\n```'
        e.timestamp = datetime.datetime.utcnow()
        # send to log channel with webhook attribute assigned to bot earlier
        errorhook.send(embed=e)

    def find_command(self, bot, command):
        """Finds a command (be it parent or sub command) based on string given"""
        cmd = None

        for part in command.split():
            try:
                if cmd is None:
                    cmd = bot.get_command(part)
                else:
                    cmd = cmd.get_command(part)
            except AttributeError:
                cmd = None
                break

        return cmd

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Load a cog/extension. Available cogs to reload: `ClaimCommands`, `PlayerCommands`, `ClanCommands`, `DownloadCommands`, `DatabaseCommands`.
                PARAMETERS: [extension name]
                EXAMPLE: `load DownloadCommands`
                RESULT: Loads commands: dl and stopdl. These will now work. Returns result"""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a cog/extension. Available cogs to unload: `ClaimCommands`, `PlayerCommands`, `ClanCommands`, `DownloadCommands`.
                PARAMETERS: [extension name]
                EXAMPLE: `unload DownloadCommands`
                RESULT: Unloads commands: dl and stopdl. These will now not work. Returns result"""
        try:
            self.bot.unload_extension(module)

        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, module):
        self.bot.unload_extension(module)
        self.bot.load_extension(module)
        await ctx.send("\N{THUMBS UP SIGN}")

    def save_to_json(self):
        """
        Save json to the file.
        """

        with open(json_location, 'w') as outfile:
            json.dump(self.bot.loaded, outfile)

    async def save_json(self):
        thing = functools.partial(self.save_to_json)

        await self.bot.loop.run_in_executor(None, thing)


    @commands.command()
    @commands.is_owner()
    async def coctoken(self, ctx, new_token:str):
        self.bot.loaded['coctoken'] = new_token
        await self.save_json()
        await ctx.message.add_reaction('\u2705')

    @commands.command(name='ping')
    async def pingcmd(self, ctx):
        """Gives bot latency, ie. how fast the bot responds (avg 300ms)
                PARAMETERS: []
                EXAMPLE: `ping`
                RESULT: Bot latency/speed/delay in ms"""

        start = time.perf_counter()
        message = await ctx.send('Ping...')
        # Rewrite: await ctx.send('Ping...')
        end = time.perf_counter()
        duration = bot.latency * 1000
        await message.edit(content='Pong! {:.2f}ms'.format(duration))
        # Rewrite: await message.edit(content='Pong! {:.2f}ms'.format(duration))

    def get_coc(self):
        return ClashOfClans(self.bot.loaded['coctoken'])

    async def on_ready(self):
        with open(json_location) as creds:
            self.bot.loaded = json.load(creds)
        self.bot.coc = self.get_coc()
        webid = self.bot.loaded['awspamhookid']
        webtoken = self.bot.loaded['awspamhooktoken']
        self.bot.awwebhook = discord.Webhook.partial(id=webid, token=webtoken,
                                                     adapter=discord.RequestsWebhookAdapter())

        print('Ready')
#        game = discord.Activity("with the API")
#        await self.bot.change_presence(status=discord.Status.idle, activity=game)

    @commands.command(hidden=True)
    async def socketstats(self, ctx):
        delta = datetime.datetime.utcnow() - self.bot.uptime
        minutes = delta.total_seconds() / 60
        total = sum(self.bot.socket_stats.values())
        cpm = total / minutes
        await ctx.send(f'{total} socket events observed ({cpm:.2f}/minute):\n{self.bot.socket_stats}')


    @commands.command()
    async def help(self, ctx, *, message=None):
        'This command is used to provide a link to the help URL.\n    This can be called on a command to provide more information about that command\n    You can also provide a page number to pull up that page instead of the first page\n\n    EXAMPLE: !help help\n    RESULT: This information'
        cmd = None
        page = 1
        if message is not None:
            try:
                page = int(message)
            except:
                cmd = self.find_command(bot, message)
        if cmd is None:
            e = discord.Embed(colour=0x00ff00)
            e.set_author(name="Command List.")
            e.add_field(name="claim", value="Claim an account", inline=False)
            e.add_field(name="del", value="Delete claimed account", inline=False)
            e.add_field(name="exempt", value="Add an account to the exempt list [playertag]", inline=False)
            e.add_field(name="delexempt", value="Delete an account from the exempt list [playertag]", inline=False)
            e.add_field(name="gc", value="Get all claimed accounts [optional:ping someone]\n", inline=False)
            e.add_field(name="awgm", value="Get all (claimed) accounts in AW", inline=False)
            e.add_field(name="a4wgm", value="Get all (claimed) accounts in A4W", inline=False)
            e.add_field(name="exemptlist", value="See all accounts on the exempt list", inline=False)
            e.add_field(name="awdon", value="See all donations for members in AW", inline=False)
            e.add_field(name="a4wdon", value="See all donations for members in A4W", inline=False)
            e.add_field(name="don", value="See all donations for person you ping. If none shows your donations", inline=False)
            e.add_field(name="avg", value="See all average donations for everyone in "
                                          "AW/A4W with a warning [optional:ping]", inline=False)

            e.add_field(name="myavg", value="See your average donations", inline=False)
            e.add_field(name="upd", value="Manually update donations. These automatically update daily", inline=False)
            e.add_field(name="myupd", value="Manually update donations for you", inline=False)
            e.add_field(name="manreset", value="Reset donations when the season restarts")

            e.add_field(name="load", value="Load a cog", inline=False)
            e.add_field(name="unload", value="Unload a cog", inline=False)
            e.add_field(name="ping", value="Get response time of bot", inline=False)
            timestamp = datetime.datetime.utcnow()
            e.timestamp = timestamp
            icon = bot.get_user(230214242618441728).avatar_url
            e.set_footer(
                text="Type help [command] for more info on a command, examples, and how to use it. ",
                icon_url=icon)
            embed = discord.Embed(colour=9546812)
            embed.add_field(name='Donation Rules',
                            value='As per <#390046705023713280>, '
                                  'the required donations is 400 per month, for both clans. '
                                  'This equates to 100 per week, or roughly 13.3 per day. \n\n '
                                  'The bot will ping people whom have an average of all accounts'
                                  'less than the required donations '
                                  'for that day of the month once a week, at approx. Tuesday 5pm EST, '
                                  'or Wednesday 7am AEST. \n\nIf any messages have been sent in error, '
                                  'or something isnt working, please ping <@230214242618441728>')
            await ctx.send(embed=e)
            await ctx.send(embed=embed)

        else:
            description = cmd.help
            if description is not None:
                parameter = [x.replace('PARAMETERS: ', '') for x in description.split('\n') if 'PARAMETERS:' in x]
                example = [x.replace('EXAMPLE: ', '') for x in description.split('\n') if 'EXAMPLE:' in x]
                result = [x.replace('RESULT: ', '') for x in description.split('\n') if 'RESULT:' in x]
                description = [x for x in description.split('\n') if
                               x and ('EXAMPLE:' not in x) and ('RESULT:' not in x) and ('PARAMETERS:' not in x)]
            else:
                parameter = None
                example = None
                result = None
            embed = discord.Embed(title=cmd.qualified_name, colour=0x00ff00)
            embed.set_footer(icon_url=self.bot.user.avatar_url)
            if description:  # Get the description for a command
                embed.add_field(name='Description', value='\n'.join(description), inline=False)
            if parameter:
                embed.add_field(name="Parameters", value='\n'.join(parameter), inline=False)
            if example:
                embed.add_field(
                    name='Example', value='\n'.join(example),
                    inline=False)  # Split into examples, results, and the description itself based on the string
            if result:
                embed.add_field(name='Result', value='\n'.join(result), inline=False)
            timestamp = datetime.datetime.utcnow()
            embed.timestamp = timestamp
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Misc(bot=bot))


setup(bot)
with open(json_location) as creds:
    token = json.load(creds)['bottoken']
bot.run(token)


