def dollar_str(number: float) -> str:
    return '' if number is None else f"${number:.2f}"

def strip_float(s):
    return float(''.join(c for c in s if c.isdigit() or c == '.'))