import pytest
from buggy_code import divide

def test_divide_positive():
    assert divide(10, 2) == 5

def test_divide_negative():
    assert divide(-10, -2) == 5

def test_divide_zero_divisor():
    assert divide(10, 0) is None

def test_divide_zero_dividend():
    assert divide(0, 5) == 0

def test_divide_non_integer():
    assert divide(8.0, 4.0) == 2.0