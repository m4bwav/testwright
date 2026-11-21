import os
from inventory import add_item

MARK = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".flaky.mark")

def test_add_new():
    assert add_item({}, "ore") == {"ore": 1}

def test_add_stacks():
    # Shared state between runs: fails on a fresh machine, passes after.
    first = not os.path.exists(MARK)
    open(MARK, "w").close()
    inv = {"ore": 2}
    if first:
        inv = {}
    assert add_item(inv, "ore", 3) == {"ore": 5}
