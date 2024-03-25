import re


def validate_lc_call_number(call_number):
    pattern = re.compile(r'^[A-Z]{1,3}.+')
    return bool(pattern.fullmatch(call_number))
