#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ahocode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/ahocode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
# The code is taken from abusix/ahocorapy:
# https://github.com/abusix/ahocorapy/blob/master/src/ahocorapy/keywordtree.py

AHOCORASICK = 2

EMPTY = 0

KEY_SEQUENCE = 200
KEY_STRING = 100

MATCH_AT_LEAST_PREFIX = 2

MATCH_AT_MOST_PREFIX = 1

MATCH_EXACT_LENGTH = 0

STORE_ANY = 30
STORE_INTS = 10
STORE_LENGTH = 20

TRIE = 1

unicode = 1

DEFAULT = object()


class State(object):
    __slots__ = ['identifier', 'symbol', 'success', 'transitions', 'parent',
                 'matched_keyword', 'longest_strict_suffix', 'value']

    def __init__(self, identifier, symbol=None, parent=None, success=False, value=None):
        self.symbol = symbol
        self.identifier = identifier
        self.transitions = {}
        self.parent = parent
        self.success = success
        self.matched_keyword = None
        self.value = value
        self.longest_strict_suffix = None

    def __str__(self):
        transitions_as_string = ','.join(
            '{0} -> {1}'.format(key, value.identifier) for key, value in self.transitions.items())
        return "State {0}. Transitions: {1}".format(self.identifier, transitions_as_string)


class Automaton:
    """
    Automaton(value_type=ahocorasick.STORE_ANY, [key_type])

    Create a new empty Automaton. Both value_type and key_type
    are optional.

    value_type is one of these constants:
    - ahocorasick.STORE_ANY [default] : The associated value can
      be any Python object.
    - ahocorasick.STORE_LENGTH : The length of an added string
      key is automatically used as the associated value stored
      in the trie for that key.
    - ahocorasick.STORE_INTS : The associated value must be a
      32-bit integer.

    key_type defines the type of data that can be stored in an
    automaton; it is one of these constants and defines type of
    data might be stored:
    - ahocorasick.KEY_STRING [default] : string
    - ahocorasick.KEY_SEQUENCE : sequences of integers
    """

    def __init__(self, value_type=STORE_ANY, key_type=KEY_STRING):
        self._zero_state = State(0)
        self._counter = 1
        self._finalized = False

        self.value_type = value_type
        self.key_type = key_type
        self._kind = EMPTY
        self._size = 0

    def add_word(self, key, value=None):
        """
        add_word(key, [value]) -> boolean

        Add a key string to the dict-like trie and associate this
        key with a value. value is optional or mandatory depending
        how the Automaton instance was created. Return True if the
        word key is inserted and did not exists in the trie or False
        otherwise. The value associated with an existing word is
        replaced.

        The value is either mandatory or optional:
        - If the Automaton was created without argument (the
          default) as Automaton() or with
          Automaton(ahocorasik.STORE_ANY) then the value is required
          and can be any Python object.
        - If the Automaton was created with
          Automaton(ahocorasik.STORE_INTS) then the value is
          optional. If provided it must be an integer, otherwise it
          defaults to len(automaton) which is therefore the order
          index in which keys are added to the trie.
        - If the Automaton was created with
          Automaton(ahocorasik.STORE_LENGTH) then associating a
          value is not allowed - len(word) is saved automatically as
          a value instead.

        Calling add_word() invalidates all iterators only if the new
        key did not exist in the trie so far (i.e. the method
        returned True).
        """

        if self._finalized:
            raise ValueError('KeywordTree has been finalized.' +
                             ' No more keyword additions allowed')
        original_keyword = key
        keyword_size = len(key)
        if self.value_type == STORE_LENGTH:
            value = keyword_size
        if len(key) <= 0:
            return
        current_state = self._zero_state
        for char_index in range(keyword_size):
            char = key[char_index]
            try:
                current_state = current_state.transitions[char]
            except KeyError:
                next_state = State(self._counter, parent=current_state,
                                   symbol=char)
                self._counter += 1
                current_state.transitions[char] = next_state
                current_state = next_state
        current_state.value = value
        if current_state.success:
            return False
        current_state.success = True
        current_state.matched_keyword = original_keyword
        self._kind = TRIE
        self._size += 1
        return True

    def clear(self):  # real signature unknown; restored from __doc__
        """
        clear()

        Remove all keys from the trie. This method invalidates all
        iterators.
        """
        self._zero_state = State(0)
        self._counter = 1
        self._finalized = False
        self._kind = EMPTY
        self._size = 0

    def exists(self, key):  # real signature unknown; restored from __doc__
        """
        exists(key) -> boolean

        Return True if the key is present in the trie. Same as using
        the 'in' keyword.
        """
        if not isinstance(key, str):
            raise Exception(f"Expected string but got {type(key)}")
        if not self._finalized:
            current_state = self._zero_state
            for char in key:
                try:
                    current_state = current_state.transitions[char]
                except KeyError:
                    return False
            return True
        else:
            self.search_all(key)

    def iter(self, string, start=None, end=None, *args, **kwargs):
        if not self._finalized:
            raise ValueError('Automaton has not been finalized. No search allowed. Call make_automaton() first.')
        zero_state = self._zero_state
        current_state = zero_state
        offset = 0
        if (start and end) != None:
            offset = start
            string = string[start:end]
        for idx, symbol in enumerate(string):
            current_state = current_state.transitions.get(
                symbol, zero_state.transitions.get(symbol, zero_state))
            state = current_state
            while state is not zero_state:
                if state.success:
                    value = state.value
                    yield idx + offset, value
                state = state.longest_strict_suffix

    def get(self, key, default=DEFAULT):
        """
        get(key[, default])

        Return the value associated with the key string.

        Raise a KeyError exception if the key is not in the trie and
        no default is provided.

        Return the optional default value if provided and the key is
        not in the trie.
        """
        current_state = self._zero_state
        for char in key:
            try:
                current_state = current_state.transitions[char]
            except KeyError:
                if default is not DEFAULT:
                    return default
                else:
                    raise KeyError(f"Key: {key} not found in trie")
        return current_state.value

    def find_all(self, string, callback, start=None, end=None):
        """
        find_all(string, callback, [start, [end]])

        Perform the Aho-Corasick search procedure using the provided
        input string and iterate over the matching tuples
        (end_index, value) for keys found in string. Invoke the
        callback callable for each matching tuple.

        The callback callable must accept two positional arguments:
        - end_index is the end index in the input string where a
        trie key string was found. - value is the value associated
        with the found key string.

        The start and end optional arguments can be used to limit
        the search to an input string slice as in string[start:end].

        Equivalent to a loop on iter() calling a callable at each
        iteration.
        """
        for idx, value in self.iter(string, start, end):
            callback(idx, value)

    def values(self, prefix=None, wildcard=None, how=None):
        for key, value in self.items():
            yield value

    def keys(self, prefix=None, wildcard=None, how=None):
        for key, value in self.items():
            yield key

    def items(self, prefix=None, wildcard=None, how=None):
        processed = set()
        zero_state = self._zero_state
        to_process = [zero_state]
        while to_process:
            state = to_process.pop()
            if state.success:
                yield state.matched_keyword, state.value
            processed.add(state.identifier)
            for child in state.transitions.values():
                if child.identifier not in processed:
                    to_process.append(child)

    def make_automaton(self):
        """
        make_automaton()

        Finalize and create the Aho-Corasick automaton based on the
        keys already added to the trie. This does not require
        additional memory. After successful creation the
        Automaton.kind attribute is set to ahocorasick.AHOCORASICK.
        """
        if self._finalized:
            raise ValueError('KeywordTree has already been finalized.')
        self._zero_state.longest_strict_suffix = self._zero_state
        self.search_lss_for_children(self._zero_state)
        self._finalized = True
        self._kind = AHOCORASICK

    def search_all(self, text):
        """
        Search a text for all occurrences of the added keywords.
        Can only be called after finalized() has been called.
        O(n) with n = len(text)
        @return: Generator used to iterate over the results.
                 Or None if no keyword was found in the text.
        """
        if not self._finalized:
            raise ValueError('KeywordTree has not been finalized. No search allowed. Call make_automaton() first.')
        zero_state = self._zero_state
        current_state = zero_state
        for idx, symbol in enumerate(text):
            current_state = current_state.transitions.get(
                symbol, zero_state.transitions.get(symbol, zero_state))
            state = current_state
            while state is not zero_state:
                if state.success:
                    keyword = state.matched_keyword
                    yield keyword, idx + 1 - len(keyword)
                state = state.longest_strict_suffix

    def search_lss_for_children(self, zero_state):
        processed = set()
        to_process = [zero_state]
        while to_process:
            state = to_process.pop()
            processed.add(state.identifier)
            for child in state.transitions.values():
                if child.identifier not in processed:
                    self.search_lss(child)
                    to_process.append(child)

    def search_lss(self, state):
        zero_state = self._zero_state
        parent = state.parent
        traversed = parent.longest_strict_suffix
        while True:
            if state.symbol in traversed.transitions and traversed.transitions[state.symbol] is not state:
                state.longest_strict_suffix = traversed.transitions[state.symbol]
                break
            elif traversed is zero_state:
                state.longest_strict_suffix = zero_state
                break
            else:
                traversed = traversed.longest_strict_suffix
        suffix = state.longest_strict_suffix
        if suffix is zero_state:
            return
        if suffix.longest_strict_suffix == None:
            self.search_lss(suffix)
        for symbol, next_state in suffix.transitions.items():
            if symbol not in state.transitions:
                state.transitions[symbol] = next_state

    def __getstate__(self):
        state_list = [None] * self._counter
        process_queue = [self._zero_state]
        while process_queue:
            state = process_queue.pop()
            transitions = {key: value.identifier for key,
            value in state.transitions.items()}
            state_list[state.identifier] = {
                'symbol': state.symbol,
                'success': state.success,
                'parent': state.parent.identifier if state.parent != None else None,
                'matched_keyword': state.matched_keyword,
                'value': state.value,
                'longest_strict_suffix': state.longest_strict_suffix.identifier if state.longest_strict_suffix != None else None,
                'transitions': transitions
            }
            for child in state.transitions.values():
                if len(state_list) <= child.identifier or not state_list[child.identifier]:
                    process_queue.append(child)

        return {
            'finalized': self._finalized,
            'counter': self._counter,
            'states': state_list
        }

    def __setstate__(self, state):
        self._counter = state['counter']
        self._finalized = state['finalized']
        states = [None] * len(state['states'])
        for idx, serialized_state in enumerate(state['states']):
            deserialized_state = State(idx, serialized_state['symbol'])
            deserialized_state.success = serialized_state['success']
            deserialized_state.matched_keyword = serialized_state['matched_keyword']
            deserialized_state.value = serialized_state['value']
            states[idx] = deserialized_state
        for idx, serialized_state in enumerate(state['states']):
            deserialized_state = states[idx]
            if serialized_state['longest_strict_suffix'] != None:
                deserialized_state.longest_strict_suffix = states[
                    serialized_state['longest_strict_suffix']]
            else:
                deserialized_state.longest_strict_suffix = None
            if serialized_state['parent'] != None:
                deserialized_state.parent = states[serialized_state['parent']]
            else:
                deserialized_state.parent = None
            deserialized_state.transitions = {
                key: states[value] for key, value in serialized_state['transitions'].items()}
        self._zero_state = states[0]

    def __len__(self):
        return self._size

    def __contains__(self, item):
        return self.exists(item)

    @property
    def kind(self):
        return self._kind
