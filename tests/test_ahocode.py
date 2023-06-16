#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/ahocode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
# Tests are taken from: WojciechMula/pyahocorasick
# https://github.com/WojciechMula/pyahocorasick/blob/master/tests

import unittest

from ahocode import ahocode


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


class TestCase(unittest.TestCase):

    def assertEmpty(self, collection):
        self.assertEqual(0, len(collection))

    def assertNotEmpty(self, collection):
        self.assertGreater(len(collection), 0)


class TestTrieStorePyObjectsBase(TestCase):

    def setUp(self):
        self.A = ahocode.Automaton()
        self.words = "word python aho corasick \x00\x00\x00".split()
        self.inexisting = "test foo bar dword".split()


class TestTrieMethods(TestTrieStorePyObjectsBase):
    "Test basic methods related to trie structure"

    def test_add_word(self):
        A = self.A
        self.assertTrue(A.kind == ahocode.EMPTY)

        n = 0
        for word in self.words:
            n += 1
            A.add_word(word, None)
            self.assertEqual(A.kind, ahocode.TRIE)
            self.assertEqual(len(A), n)

        # dupliacted entry
        A.add_word(self.words[0], None)
        self.assertTrue(A.kind == ahocode.TRIE)
        self.assertTrue(len(A) == n)

    def test_add_empty_word(self):
        if ahocode.unicode:
            self.assertFalse(self.A.add_word("", None))
        else:
            self.assertFalse(self.A.add_word(b"", None))

        self.assertEqual(len(self.A), 0)
        self.assertEqual(self.A.kind, ahocode.EMPTY)

    def test_clear(self):
        A = self.A
        self.assertTrue(A.kind == ahocode.EMPTY)

        for w in self.words:
            A.add_word(w, w)

        self.assertEqual(len(A), len(self.words))

        A.clear()
        self.assertEqual(A.kind, ahocode.EMPTY)
        self.assertEqual(len(A), 0)

    def test_exists(self):
        A = self.A

        for w in self.words:
            A.add_word(w, w)

        for w in self.words:
            self.assertTrue(A.exists(w))

        for w in self.inexisting:
            self.assertFalse(A.exists(w))

    def test_contains(self):
        A = self.A
        for w in self.words:
            A.add_word(w, w)

        for w in self.words:
            self.assertTrue(w in A)

        for w in self.inexisting:
            self.assertTrue(w not in A)

    def test_get1(self):
        A = self.A
        for i, w in enumerate(self.words):
            A.add_word(w, i + 1)

        for i, w in enumerate(self.words):
            self.assertEqual(A.get(w), i + 1)

    def test_get2(self):
        A = self.A
        for i, w in enumerate(self.words):
            A.add_word(w, i + 1)

        for w in self.inexisting:
            self.assertEqual(A.get(w, None), None)

    def test_get3(self):
        A = self.A
        for i, w in enumerate(self.words):
            A.add_word(w, i + 1)

        for w in self.inexisting:
            with self.assertRaises(KeyError):
                A.get(w)

    def test_get_from_an_empty_automaton(self):
        A = ahocode.Automaton()

        r = A.get('foo', None)
        self.assertEqual(r, None)
