import time
import datetime

def convert_date_to_timestamp(target_date):
    """
    datetime.date 날짜를 타임스탬프로 변환
    """
    timestamp = int(time.mktime(datetime.datetime(
        target_date.year, target_date.month, target_date.day, 9, 0).timetuple()))

    return timestamp
