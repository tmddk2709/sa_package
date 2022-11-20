import re

def convert_hannum_to_num(hannum, is_int=False):
    """
    한글 형태로 표시된 숫자 아라비아 숫자로 변환
    """

    num_only_regex = re.compile("[\d.\-\+]")
    result_num = num_only_regex.findall(hannum)
    result_num = "".join(result_num)

    not_num_regex = re.compile("[백만천억]")
    digit = not_num_regex.findall(hannum)
    digit = "".join(digit)

    if digit == "십억":
        digit = 1000000000
    elif digit == "백만":
        digit = 1000000
    elif digit == "만":
        digit = 10000
    elif digit == "천":
        digit = 1000
    else:
        digit = 1

    if result_num in ["", "-"]:
        return ""

    if is_int:
        return int(digit*float(result_num))
    else:
        return digit*float(result_num)


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