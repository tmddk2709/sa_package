import datetime

def first_day_of_month(any_day):    
    return any_day.replace(day=1)


def last_day_of_month(any_day):
    # this will never fail
    # get close to the end of the month for any day, and add 4 days 'over'
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
    return next_month - datetime.timedelta(days=next_month.day)


def first_day_of_week(any_day):
    return any_day - datetime.timedelta(days=any_day.weekday())


def last_day_of_last_week(any_day=None):
    if any_day is None:
        any_day = datetime.date.today()
    
    return any_day - datetime.timedelta(days=any_day.weekday()+1)  # 이전 주 일요일