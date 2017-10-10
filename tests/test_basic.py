# -*- coding: utf-8 -*-

from .context import psox

import unittest



class TypesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_psox_types_000_Sox(self) :
        Sox = psox.types.Sox 
        assert Sox() == ()
        assert Sox(None) == Sox()
        assert Sox(1) == ('1',)
        assert Sox(12) == ('12',)
        assert Sox('a','b','c') == ('a','b','c')
        assert Sox('a b c') == Sox('a','b','c')
        assert Sox('a b','c') == Sox('a','b','c')
        assert Sox(Sox(1,2)) == Sox(1,2)
        assert Sox(1,2,3) == Sox('1 2 3')

class CoreTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_psox_core_000_main(self) :
        self.assertIsNone(None)

if __name__ == '__main__':
    unittest.main()
