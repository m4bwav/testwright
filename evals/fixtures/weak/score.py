def score(hits, misses):
    if hits + misses == 0:
        return 0
    return round(100 * hits / (hits + misses))
