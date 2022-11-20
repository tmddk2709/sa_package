def convert_sec_to_hhmmss_format(sec):
    """
    초를 hh:mm:ss 포맷으로 변환
    """

    hh = sec // 3600
    mm = (sec % 3600) // 60
    ss = sec % 60

    if hh == 0:
        return f"{mm}:{ss:02}"
    else:
        return f"{hh}:{mm:02}:{ss:02}"


        
def convert_hhmmss_format_to_sec(hhmmss):
    """
    hh:mm:ss 포맷을 초로 변경
    """

    if ":" not in hhmmss:
        return hhmmss

    # hh:mm:ss format -> seconds
    hms = hhmmss.split(":")

    unit = 1
    seconds = 0
    for t in hms[::-1]:
        seconds += int(t)*unit
        unit *= 60

    return seconds


def convert_hm_format_to_min(hm):
    """
    00h 00m 포맷을 분으로 변경
    """

    hours = hm.split('h')[0]
    mins = hm.split('h')[1].split('m')[0]
    if mins == "":
        mins = 0

    return float(hours)*60 + float(mins)