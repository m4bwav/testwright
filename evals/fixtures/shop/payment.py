def charge(card, cents, balance):
    if cents <= 0:
        raise ValueError("amount")
    if balance < cents:
        return False, balance
    return True, balance - cents

def refund(order, cents):
    order["refunded"] = order.get("refunded", 0) + cents
    return order
