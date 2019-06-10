import datetime


def get_this_month():
    return datetime.date.today().strftime('%B %y').lower()


def get_last_month():
    month = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    return month.strftime('%B %y').lower()


def get_this_year():
    return datetime.date.today().strftime('%y')
