import time
import datetime


def get_after_30_days_timestamp():
    today_after_30_day = datetime.datetime.now() + datetime.timedelta(days=30)
    today_after_30_day_timestamp = today_after_30_day.timestamp()

    return today_after_30_day_timestamp


def get_today_timestamp():
    today = datetime.datetime.now()
    today -= datetime.timedelta(hours=today.hour, minutes=today.minute, seconds=today.second, microseconds=today.microsecond)
    today_timestamp = today.timestamp()

    return today_timestamp


def get_after_n_minutes_timestamp(minutes):
    today_after_n_minutes = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    today_after_n_minutes_timestamp = today_after_n_minutes.timestamp()

    return today_after_n_minutes_timestamp


if __name__ == '__main__':
    a = get_after_30_days_timestamp()
    print(a, type(a))
