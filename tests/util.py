import unittest
from app.util import *

# Help for unittests see: https://docs.python.org/3/library/unittest.html


class TestSortString(unittest.TestCase):
    """
    This class contains test for the function app.util.sortString
    """

    def test_empty(self):
        """
        Test with empty string.
        """
        self.assertEqual(sortString(""), "")

    def test_singleton(self):
        """
        Test with a single character string.
        """
        self.assertEqual(sortString("x"), "x")

    def test_ident(self):
        """
        Test if a sorted string will be unchanged.
        """
        self.assertEqual(sortString("abcdef"), "abcdef")
        self.assertEqual(sortString("ABCDEF"), "ABCDEF")
        self.assertEqual(sortString("ABCdef"), "ABCdef")

    def test_lower_reversed(self):
        """
        Test if a reversed string will get sorted.
        """
        self.assertEqual(sortString("lkjihg"), "ghijkl")
        self.assertEqual(sortString("LKJIHG"), "GHIJKL")

    def test_mixed(self):
        """
        Test if a mixed upercase/lowercase will get sorted correctly.
        """
        self.assertEqual(sortString("LkJiHg"), "HJLgik")

