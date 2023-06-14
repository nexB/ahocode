#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import subprocess
import unittest
import configparser
import ahocode


class test_automaton_methods(unittest.TestCase):
    def test_find_all(self):
        automaton = ahocode.Automaton()
        words = "he e hers his she hi him man he".split()
        #        0  1  2    3   4   5  6   7   8
        for i, w in enumerate(words):
            automaton.add_word(w, (i, w))
        query = "he rshershidamanza "
        #        01234567890123
        automaton.make_automaton()

        assert query[2:8] == ' rsher'
        results = list(automaton.iter(string=query, start=2, end=8))
        assert results == [(6, (4, 'she')), (6, (8, 'he')), (6, (1, 'e'))]

        res = []

        def callback(index, item):
            res.append(dict(index=index, item=item))

        assert query[2:11] == ' rshershi'
        automaton.find_all(query, callback, 2, 11)

        expected = [
            {'index': 6, 'item': (4, 'she')},
            {'index': 6, 'item': (8, 'he')},
            {'index': 6, 'item': (1, 'e')},
            {'index': 8, 'item': (2, 'hers')},
            {'index': 10, 'item': (5, 'hi')},
        ]

        assert res == expected

    def test_item_keys_values(self):
        automaton = ahocode.Automaton()
        words = 'he e hers his she hi him man he'.split()
        #         0 1    2   3   4  5   6   7  8
        for i, w in enumerate(words):
            automaton.add_word(w, (i, w))

        expected_keys = ['man', 'she', 'e', 'hi', 'him', 'his', 'he', 'hers']

        expected_values = [
            (7, 'man'),
            (4, 'she'),
            (1, 'e'),
            (5, 'hi'),
            (6, 'him'),
            (3, 'his'),
            (8, 'he'),
            (2, 'hers'),
        ]

        assert sorted(automaton.keys()) == sorted(expected_keys)
        assert sorted(automaton.values()) == sorted(expected_values)
        assert sorted(dict(automaton.items()).values()) == sorted(expected_values)
        assert sorted(dict(automaton.items()).keys()) == sorted(expected_keys)

        automaton.make_automaton()

        assert sorted(automaton.keys()) == sorted(expected_keys)
        assert sorted(automaton.values()) == sorted(expected_values)
        assert sorted(dict(automaton.items()).values()) == sorted(expected_values)
        assert sorted(dict(automaton.items()).keys()) == sorted(expected_keys)