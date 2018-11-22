import calendar
import datetime
import RoutineUpdates

upd = RoutineUpdates.AllUpdates()

def start():
    cal = calendar.Calendar(0)
    month = cal.monthdatescalendar(datetime.date.today().year, datetime.date.today().month)
    lastweek = month[-1]
    monday = lastweek[0]
    if datetime.date.today() == monday:
        upd.man_reset()
        upd.upd()
        upd.upd_donationsbytoday()
        upd.refresh_avg()


start()


