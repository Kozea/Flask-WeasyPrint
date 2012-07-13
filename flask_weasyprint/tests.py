# coding: utf8
"""
    Tests for Flask-WeasyPrint
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.

"""

import unittest

import flask_weasyprint


class TestFlaskWeasyPrint(unittest.TestCase):
    def test_import(self):
        assert flask_weasyprint.HTML.__module__ == 'weasyprint'


if __name__ == '__main__':
    unittest.main()
