def quote(qty, member=False, code=None):
    p = qty * 499
    if qty >= 10:
        p = p * 9 / 10
    if member:
        p -= 100
    if code == "HALF":
        p = p / 2
    if p < 0:
        p = 0
    return int(p)
