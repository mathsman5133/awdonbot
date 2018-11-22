import discord
from discord import Webhook, RequestsWebhookAdapter
import sqlite3
from creds import awwebid, awwebtoken

conn = sqlite3.connect('/home/pi/Desktop/awdonbot/mathsbots.db')
c = conn.cursor()
awhook = Webhook.partial(awwebid, awwebtoken, adapter=RequestsWebhookAdapter())


def donationbytoday():
    c.execute("SELECT donationsbytoday FROM season WHERE toggle = 1")
    dump = c.fetchall()
    for donbytod in dump:
        return int(donbytod[0])


def avg():
    c.execute("SELECT averagedonations, userid FROM averages WHERE warning = 'Yes'")
    dump = c.fetchall()
    send1 = ''
    ping = ''
    for info in dump:
        avgdon = info[0]
        id = f'<@{info[1]}>'
        ping += id + ', '
        line = ''
        line += '{:>0} Avg Don Dif:'.format(id)
        line += '{:>12}'.format(avgdon) + '\n\n'
        send1 += line
    embed = discord.Embed(colour=9546812)
    embed.title = 'Average Donation List - Warnings only'
    embed.description = send1
    awhook.send(embed=embed)
    awhook.send(
         f'{ping}\nThe average donations of all your accounts currently have '
         f'less than the required: {str(donationbytoday())} troop space by today. '
         f'\nPlease find your IGN above and donate some troops! '
         f'\nIf you want to check your donations, please type `don` and `avg` in <#462931331308060673>. ')
    embedhelp = discord.Embed(colour=9546812)
    embedhelp.add_field(name='Donation Rules',
                        value='As per <#390046705023713280>, '
                              'the required donations is 400 per month, for both clans. '
                              'This equates to 100 per week, or roughly 13.3 per day. \n\n '
                              'The bot will ping people whom have an average of all accounts'
                              'less than the required donations '
                              'for that day of the month once a week, at approx. Tuesday 5pm EST, '
                              'or Wednesday 7am AEST. \n\nIf any messages have been sent in error, '
                              'or something isnt working, please ping <@230214242618441728>')
    awhook.send(embed=embedhelp)


avg()

