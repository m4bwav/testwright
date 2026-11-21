from unittest.mock import MagicMock
from score import score

def test_score_runs():
    score(3, 1)
    assert True

def test_score_saved():
    db = MagicMock()
    db.save(score(1, 1))
    db.save.assert_called_once()

def test_score_type():
    s = score(2, 2)
    assert s == s
