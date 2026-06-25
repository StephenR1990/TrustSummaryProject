#some basic automated testing
import unittest
from main import check_int


#test the integer check function
class TestIntegerCheck(unittest.TestCase):
    def test_check_int_valid(self):
        self.assertEqual(check_int("5"), 5)
    
    def test_check_int_invalid(self):
        self.assertEqual(check_int("abc"), 0)
    
    def test_check_int_negative(self):
        self.assertEqual(check_int("-1"), -1)

    def test_check_int_negative(self):
        self.assertEqual(check_int("5.2"), 5.2)

