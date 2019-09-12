import datetime


def get_this_month() -> str:
    return datetime.date.today().strftime('%B %y').lower()


def get_last_month() -> str:
    month = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    return month.strftime('%B %y').lower()


def get_this_year() -> str:
    return datetime.date.today().strftime('%y')
