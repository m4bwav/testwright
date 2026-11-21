from cart import total

def test_total_plain():
    assert total([100, 250]) == 350

def test_total_discount():
    assert total([200], discount_pct=10) == 180
