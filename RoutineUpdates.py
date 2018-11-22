import sqlite3
import datetime
from discord import Webhook, RequestsWebhookAdapter
import os
import json

json_location = os.path.join(os.getcwd(), 'creds.json')

with open(json_location) as creds:
    creds = json.load(creds)
    coctoken = creds['coctoken']
    awbotspamid = creds['spamhookid']
    awbotspamtoken = creds['spamhooktoken']

db_path = os.path.join(os.getcwd(), 'mathsbots.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

awbotspamhook = Webhook.partial(awbotspamid, awbotspamtoken, adapter=RequestsWebhookAdapter())


class AllUpdates:
    def __init__(self):
        pass

    def donationbytoday(self):
        c.execute("SELECT donationsbytoday FROM season WHERE toggle = 1")
        dump = c.fetchall()
        for donbytod in dump:
            return int(donbytod[0])

    def upd_donationsbytoday(self):
        dayofyear = datetime.datetime.utcnow().strftime('%j')
        c.execute("SELECT startdate FROM season WHERE toggle = 1")
        dump = c.fetchall()
        for startdate in dump:
            datedif = int(dayofyear) - int(startdate[0])
        donreq = datedif * 13.33
        with conn:
            c.execute("UPDATE season SET donationsbytoday = :donreq", {'donreq':donreq})

    def updclandb(self, don, dif, warn, clan, tag):
        with conn:
            c.execute(
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

    def upd(self):
        c.execute('SELECT tag FROM aw')
        tags = c.fetchall()
        for tag1 in tags:
            tag = tag1[0]
            player = coc.players('{}'.format(tag)).get()
            for achievement in player['achievements']:
                if achievement['name'] == 'Friend in Need':
                    don = achievement['value']
            c.execute("SELECT donations FROM aw WHERE tag = :tag", {'tag':tag})
            dump = c.fetchall()
            for donations in dump:
                starting_donations = donations[0]
            achdif = int(don) - int(starting_donations)
            dif = str(self.donationbytoday() - achdif)
            try:
                clan = '{}'.format(player['clan']['name'])
            except KeyError:
                clan = ''
            if achdif <= self.donationbytoday():
                warn = 'Yes'
            if achdif >= self.donationbytoday():
                warn = 'No'
            self.updclandb(don, dif, warn, clan, tag)
            self.refresh_avg()
        awbotspamhook.send(
            "All players' donations have been updated. You can now type `mydon`, `awdon` or `a4wdon` to see respective donations.")

    def refresh_avg(self):
        c.execute('drop table averages')
        conn.commit()
        c.execute('CREATE TABLE `averages` '
                         '( `userid` INTEGER, `averagedonations` INTEGER, `warning` TEXT )')
        conn.commit()
        c.execute("select userid from aw where clan = 'Aussies 4 War' or clan = 'Aussie Warriors'")
        dump = list(set(c.fetchall()))
        for a in dump:
            self.new_avg(a[0])

    def new_avg(self, userid):
        c.execute("SELECT difference FROM aw WHERE userid = :id", {'id':userid})
        dump = c.fetchall()
        total_difference = 0
        for acctdon in dump:
            total_difference += int(acctdon[0])
        avg = -(int(total_difference / len(dump)))
        if avg >= self.donationbytoday():
            warn = 'No'
        else:
            warn = 'Yes'
        with conn:
            c.execute("INSERT INTO averages VALUES(:userid,:avg,:warn)", {'avg':avg, 'warn':warn, 'userid':userid})
            conn.commit()

    def new_month(self):
        dayofyear = datetime.datetime.now().strftime('%j')
        with conn:
            c.execute("INSERT INTO season VALUES (:toggle, :donbytod, :startdate)", {'toggle': 1, 'donbytod': 13.3, 'startdate': dayofyear})

    def dlstartingdonations(self, tag):
        memberinfo = coc.players(tag).get()
        achievements = memberinfo['achievements']
        for achievement in achievements:
            if achievement['name'] == 'Friend in Need':
                troopsdon = achievement['value']
                with conn:
                    c.execute("UPDATE aw SET donations=:don WHERE tag = :tag", {'don': troopsdon, 'tag': tag})

    def man_reset(self):
        with conn:
            c.execute("UPDATE season SET toggle = 0")
            c.execute("SELECT tag FROM aw")
            dump = c.fetchall()
        self.new_month()
        for tag in dump:
            self.dlstartingdonations(tag[0])
        self.upd()
        self.refresh_avg()
        awbotspamhook.send("Monthly donation dump completed")

