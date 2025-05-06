# -*- coding: utf-8 -*-

import unittest
import pathlib
import psox

from . import locator

SAMPLES = [
    locator.location / 'data' / filename
    for filename in ('newfile.raw', 'new file.raw', 'directory')
]

# -- initialisation tests
for filename in SAMPLES :
    if filename.is_file() :
        filename.unlink()
    if filename.name == 'directory' :
        filename.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------

class SoxtypesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self) :
        pass

    def tearDown(self) :
        pass

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

    def test_psox_soxtypes_001_File(self) :
        from psox.soxtypes import Sox, File, NewFile, Null

        assert Null() == Sox('-n')
        assert File('-n') == Null()
        assert NewFile('-n') == Null()
        assert File('-') == Sox('-')
        assert NewFile('-') == Sox('-')

        for filepath in map(str, SAMPLES) :
            assert File(filepath) == Null(), "file not exists"
            assert NewFile(filepath) == File(filepath), 'file creation'
            assert NewFile(filepath, overwrite=True) == File(filepath), 'create file again with overwrite'
            assert NewFile(filepath) == Null(), 'create file again with no overwrite'

class CoreTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self) :
        pass

    def tearDown(self) :
        pass

    def test_psox_core_000_main(self) :
        self.assertIsNone(None)

if __name__ == '__main__':
    unittest.main()
