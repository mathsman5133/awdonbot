import discord
from discord.ext import commands
from coc import ClashOfClans
import aiosqlite

coc = ClashOfClans('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImYzMzVkNDk5LWRjNmUtNGVmMS1iYmJiLTI3NTUwNzE2MWY0ZSIsImlhdCI6MTUzODgyNDIzNCwic3ViIjoiZGV2ZWxvcGVyL2M3YTNjN2RjLWIxMmYtZTUzZi05NmY4LWNlYjhhNDZiOGMxZSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjQ5LjE4MC4xNDYuMzEiXSwidHlwZSI6ImNsaWVudCJ9XX0.k8ZLwVV0eA63o9LW7EViPit7yaxRJESMzSJqXvRCEKBthgQp0BAMHY4d02fQ-bHou8-MmRy-HvDqG2FYR2JX_A')


class DownloadWar:
    def __init__(self, clantag):
        self.clantag = clantag

    def fromapi(self):
        current_war = coc.clans(self.clantag).get()


DownloadWar()

