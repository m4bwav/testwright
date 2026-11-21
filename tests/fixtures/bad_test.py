from unittest.mock import MagicMock

def test_nothing():
    assert True

def test_mock_only():
    m = MagicMock()
    m.save()
    m.save.assert_called_once()

def test_no_assert():
    x = 1 + 1

def test_good():
    assert add(1, 2) == 3
