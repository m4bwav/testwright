def add_item(inv, name, n=1):
    inv[name] = inv.get(name, 0) + n
    return inv
