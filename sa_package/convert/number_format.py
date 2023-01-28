import re

def convert_hannum_to_num(hannum, is_int=False):
    """
    한글 형태로 표시된 숫자 아라비아 숫자로 변환
    """

    num_only_regex = re.compile("[\d.\-\+]")
    result_num = num_only_regex.findall(hannum)
    result_num = "".join(result_num)

    not_num_regex = re.compile("[십백천만억]")
    digit = not_num_regex.findall(hannum)
    digit = "".join(digit)

    num_digit = 1
    for d in digit:
        if d == "십":
            num_digit *= 10
        elif d == "백":
            num_digit *= 100
        elif d == "천":
            num_digit *= 1000
        elif d == "만":
            num_digit *= 10000
        elif d == "억":
            num_digit *= 100000000

    if result_num in ["", "-"]:
        return ""

    if is_int:
        return int(num_digit*float(result_num))
    else:
        return num_digit*float(result_num)


def convert_engnum_to_num(hannum, is_int=False):
    """
    영어 형태로 표시된 숫자 아라비아 숫자로 변환
    """

    num_only_regex = re.compile("[\d.\-\+]")
    result_num = num_only_regex.findall(hannum)
    result_num = "".join(result_num)

    not_num_regex = re.compile("[MK]")
    digit = not_num_regex.findall(hannum)
    digit = "".join(digit)

    if digit == "M":
        digit = 1000000
    elif digit == "K":
        digit = 1000
    else:
        digit = 1

    if result_num in ["", "-"]:
        return ""

    if is_int:
        return int(digit*float(result_num))
    else:
        return digit*float(result_num)