# -*- coding: utf-8 -*-

import unittest
import os
import psox

try :
    os.unlink('data/tests/newfile.raw')
    os.unlink('data/tests/new file.raw')
    os.makedirs('data/tests/directory')
except :
    pass

class SoxtypesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_psox_soxtypes_000_Sox(self) :
        from psox.soxtypes import Sox

        assert Sox() == ()
        assert Sox(None) == Sox()
        assert Sox(1) == ('1',)
        assert Sox(12) == ('12',)
        assert Sox('a','b','c') == ('a','b','c')
        assert Sox('a b c') == Sox('a','b','c')
        assert Sox('a b','c') == Sox('a','b','c')
        assert Sox(Sox(1,2)) == Sox(1,2)
        assert Sox(1,2,3) == Sox('1 2 3')

    def test_psox_soxtypes_000_File(self) :
        from psox.soxtypes import Sox, File, NewFile, Null

        assert Null() == Sox('-n')
        assert File('-n') == Null()
        assert NewFile('-n') == Null()
        assert File('-') == Sox('-')
        assert NewFile('-') == Sox('-')

        for filepath in ['data/tests/newfile.raw',
            'data/tests/new file.raw', 'data/tests/directory'] :
            assert File(filepath) == Null()
            assert NewFile(filepath) == File(filepath)
            assert NewFile(filepath, overwrite=True) == File(filepath)
            assert NewFile(filepath) == Null()

class CoreTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_psox_core_000_main(self) :
        self.assertIsNone(None)

if __name__ == '__main__':
    unittest.main()
