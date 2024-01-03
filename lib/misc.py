import datetime as dt
from models import Today


def get_today():
    today = dt.datetime.now()
    current_week = today.isocalendar()[1]
    day_of_week = today.weekday() + 1
    today = Today(
        date=str(today.date()),
        week=current_week,
        day_of_week=day_of_week
    )
    return today
