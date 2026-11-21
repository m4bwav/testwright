def total(prices, discount_pct=0):
    subtotal = sum(prices)
    return subtotal - subtotal * discount_pct // 10
