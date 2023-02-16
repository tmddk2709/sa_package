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



def convert_iso_8859_to_sec(iso:str) -> int:
    """
    convert iso 8601 time format to seconds
    """

    sec = 0
    cur_type = "date"
    cur_num = ""

    for c in iso:
        if c == "P":
            pass
        elif c == "T":
            cur_type = "time"

        elif c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            cur_num += c
        
        elif c == "Y":
            sec += int(cur_num) * 365 * 24 * 3600
            cur_num = ""

        elif c == "M":
            if cur_type == "date":
                sec += int(cur_num) * 30 * 24 * 3600
            else:
                sec += int(cur_num) * 60

            cur_num = ""
        
        elif c == "D":
            sec += int(cur_num) * 24 * 3600
            cur_num = ""

        elif c == "H":
            sec += int(cur_num) * 3600
            cur_num = ""
        
        elif c == "S":
            sec += int(cur_num)
            cur_num = ""


    return int(sec)