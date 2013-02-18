#!/bin/env python3

from copy import deepcopy
from itertools import product

"""
nfsm.py - Nondeterministic finite state machine.
"""

class NFSM:
    """This class implements a non-deterministic finite state machine that
    matches a string of fixed, finite length. It is initialized with a string
    representing a regular expression, and an alphabet.

    Initialized objects have an internal state of "slots". Each slot represents
    a single character in the string to match, but each slot object holds a set
    of possible characters from the alphabet that could possibly belong in the
    slot given the constraints.

    This doesn't support full regular expression syntax. Non-exausted list of
    things that are not supported and will result in undefined behavior:
    * Only a single level of parenthesis allowed. No nesting.
    * A reference to a group that may or may not be matched under all
      circumstances
    * A group that is quantified or repeated
    * A reference to a forward group or a reference to a group from within the
      group

    """
    def __init__(self, regex, length, alphabet):
        # The finite state machine is represented as a number of "chains". Each
        # chain is a list of sets. Each set is a set of characters that could
        # go in that slot. For example, the regex 'AB+[^B]*' of length 4 over the
        # alphabet ABC would be represented with
        # [
        #   [set('A'), set('B'), set('B'), set('B')],
        #   [set('A'), set('B'), set('B'), set('AC')],
        #   [set('A'), set('B'), set('AC'), set('AC')],
        # ]
        # When constraints are added, the constraint set is intersected with
        # that index of each chain. If any chain has an empty set, it is
        # removed from consideration.
        self.chains = []
        self.length = length
        self.alphabet = frozenset(alphabet)

        unflattened_chains = list(self._parse_regex_part(regex))

        #print("{0!r} → {1}".format(regex, unflattened_chains))

        # Derefernce backrefereces and flatten chains
        for chain in unflattened_chains:
            # Flatten and dereference this chain, then add it to self.chains
            groups = []
            flattened = []
            for item in chain:
                if isinstance(item, list):
                    flattened.extend(item)
                    groups.append(item)
                else:
                    flattened.append(item)

            dereferenced = []
            for item in flattened:
                if isinstance(item, int):
                    dereferenced.extend(groups[item])
                else:
                    dereferenced.append(item)

            self.chains.append(dereferenced)
        #print("{0!r} → {1}".format(regex, self.chains))

        # and, since we are given the length of the string we match...
        self.chains = [chain for chain in self.chains if len(chain) == self.length]

        #print("{0!r} → {1}".format(regex, self.chains))

    def _parse_regex_part(self, regex):
        """This recursive method takes a regex and parses it, yielding a series
        of chain lists that together match this regex

        Each chain returned is a list. Each item in the list may be one of
        three things:
        * A set containing the elements from the alphabet which this slot may
          contain
        * An integer referring to a group number from a group previously
          defined
        * A list of one or more of the above denoting a group definition

        """
        if not regex:
            # Base case, an empty chain
            yield []
            return

        # Take care of union'd expressions here, first
        paren_level = 0
        index = 0
        while index < len(regex):
            c = regex[index]
            if c == "(":
                paren_level += 1
            elif c == ")":
                paren_level -= 1

            if c == "|" and paren_level == 0:
                # Here's where a yield from statement added in python 3.3 would
                # come in handy
                # Left side
                for chain in self._parse_regex_part(regex[:index]):
                    yield chain
                # Right side
                for chain in self._parse_regex_part(regex[index+1:]):
                    yield chain
                return
            index += 1

        if paren_level != 0:
            raise ValueError("Unbalanced parentheses! {0!r}".format(regex))

        # From this point on, we don't have to worry about unioned (|)
        # expressions. Just try and handle one thing.

        c = regex[0]
        end_index = 0
        group = False
        
        if c in self.alphabet:
            chains = [[set(c)]]
        elif c == ".":
            chains = [[set(self.alphabet)]]
        elif c == "[":
            end_index = regex.find("]")
            if regex[1] == "^":
                chains = [[set(self.alphabet - set(regex[2:end_index]))]]
            else:
                chains = [[set(regex[1:end_index])]]

        elif c == "(":
            # XXX Assume no nested parens for now
            end_index = regex.find(")")
            chains = list(self._parse_regex_part(regex[1:end_index]))
            group = True

        elif c == "\\":
            # A group reference
            end_index = 1
            matchindex = int(regex[1])-1
            # instead of a set or a chain, emit a chain with one integer, which
            # will be dereferenced later
            chains = [[matchindex]]

        else:
            raise ValueError("Found char {0!r} not in the alphabet or recognized regex special char".format(c))


        # At this point, the chains list is a list of chains (a chain is a list
        # of sets) representing the possible matches of the regex up to
        # end_index. This may be quantified, so take care of that
        if len(regex) > end_index+1:
            quantifier = regex[end_index+1]

            if quantifier == "*":
                # Kleene star. slot can appear zero or more times
                for chain2 in self._parse_regex_part(regex[end_index+2:]):
                    for repeatnum in range(self.length+1):
                        for chain1 in chains:
                            yield self._copy_chain(chain1, repeat=repeatnum) + self._copy_chain(chain2)
                return
            elif quantifier == "+":
                for chain2 in self._parse_regex_part(regex[end_index+2:]):
                    for repeatnum in range(1, self.length+1):
                        for chain1 in chains:
                            yield self._copy_chain(chain1, repeat=repeatnum) + self._copy_chain(chain2)
                return
            elif quantifier == "?":
                for chain2 in self._parse_regex_part(regex[end_index+2:]):
                    for chain1 in chains:
                        yield self._copy_chain(chain2)
                        yield self._copy_chain(chain1) + self._copy_chain(chain2)
                return
            # If the character was not one of the above, fall off this if
            # statement and continue below

        # If the code gets here, the handled item was not quantified
        # XXX Assumption: only unquantified parenthesized expressions can be
        # groups
        for chain2 in self._parse_regex_part(regex[end_index+1:]):
            for chain1 in chains:
                if group:
                    # the chains in the chains var are part of a group.
                    # enclose it in a list to marke it as a group. chains will
                    # be flattened and group references dereferenced later.
                    yield [self._copy_chain(chain1)] + self._copy_chain(chain2)
                else:
                    yield self._copy_chain(chain1) + self._copy_chain(chain2)
        

    @staticmethod
    def _copy_chain(chain, repeat=1):
        """Takes a chain and returns a copy of it, repeated the given number of
        times
        
        """
        if not isinstance(chain, list):
            raise ValueError("Given item is not a chain. Chains are lists")
        chaincopy = []
        for _ in range(repeat):
            for item in chain:
                chaincopy.append(deepcopy(item))
        return chaincopy

    def constrain_slot(self, index, charset):
        """constrain_slot takes a slot index and a set of characters
        indicating that slot, from some exteral source of knowledge, is one of
        the given elements.  This object is then updated and its own slots are
        adjusted to be consistent with that data.

        """
        newchains = []
        for chain in self.chains:
            chain[index] &= charset

            if chain[index]:
                newchains.append(chain)
        self.chains = newchains

    def peek_slot(self, index):
        """peek_slot takes a slot index, and returns the set of characters that
        this object currently thinks are possible to go in that slot, according
        to the regex and the constraints placed upon it.

        """
        candidates = set()
        for chain in self.chains:
            candidates |= chain[index]

        return candidates

    def match(self, matchstr):
        """Takes a string and returns True or False if it matches this regex,
        including the constraints previously placed on it with constrain_slot()
        
        """
        if len(matchstr) != self.length:
            return False

        # The string needs to match at least one of the chains. We implement
        # this as a series of constraints, but since we mutate the object we
        # need to make a copy
        newregex = self.copy()
        for i, c in enumerate(matchstr):
            newregex.constrain_slot(i, set(c))

        return bool(newregex.chains)

    def copy(self):
        """Makes a copy of this regex object, including any constraints already
        applied

        """
        newobj = self.__class__(".*", self.length, self.alphabet)

        newobj.chains = []
        for chain in self.chains:
            # Copy each set, but we need to make sure to keep aliased
            # references intact.
            newchain = []
            # maps the id() of old sets to the new copy of that set, so we can
            # re-use it when we encounter the original again.
            ids = {}

            for oldset in chain:
                if id(oldset) in ids:
                    newchain.append(ids[id(oldset)])
                else:
                    newset = set(oldset)
                    newchain.append(newset)
                    ids[id(oldset)] = newset

            newobj.chains.append(newchain)

        return newobj 
