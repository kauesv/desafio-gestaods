import datetime

def get_start_and_end_date_of_the_week():
    date = datetime.date.today()
    start_of_week = date - datetime.timedelta(date.weekday() +1)
    weekend = start_of_week + datetime.timedelta(6)
    # weekend = start_of_week + datetime.timedelta(7)
    return start_of_week, weekend


def get_date_yesterday():
    yesterday = datetime.date.today() - datetime.timedelta(1)
    # weekend = start_of_week + datetime.timedelta(7)
    return yesterday