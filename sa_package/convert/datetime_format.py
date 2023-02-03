from __future__ import annotations

import time
import datetime


def convert_datetime_to_timestamp(target_date:datetime.datetime | datetime.date):
    """
    datetime.datetime 혹은 datetime.date 를 타임스탬프로 변환
    """

    assert isinstance(target_date, datetime.datetime) or isinstance(target_date, datetime.date), "잘못된 타입 입력"

    if isinstance(target_date, datetime.datetime):
        timestamp = int(time.mktime(datetime.datetime(target_date.year, target_date.month, target_date.day, target_date.hour, target_date.minute, target_date.second).timetuple()))

    elif isinstance(target_date, datetime.date):
        timestamp = int(time.mktime(datetime.datetime(target_date.year, target_date.month, target_date.day, 9, 0, 0).timetuple()))

    return timestamp
