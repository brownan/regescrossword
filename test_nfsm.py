import unittest
import string
from copy import deepcopy
import re
from itertools import product

from nfsm import NFSM

class TestNFSMBase(unittest.TestCase):
    def assert_no_references(self, r):
        """For regexes that have no backreferences, each set must be unique, so
        call this to verify that

        """
        ids = set()
        for chain in r.chains:
            for s in chain:
                self.assertNotIn(id(s), ids, msg="set {0} in chain {1}".format(s, chain))
                ids.add(id(s))

class TestBasics(TestNFSMBase):
    """Tests the basic matching mechanisms. Each test here involves only one
    chain.

    """
    def test_literal(self):
        r = NFSM("A", 1, "ABC")
        self.assert_no_references(r)

        self.assertEqual([[set("A")]], r.chains)

    def test_dot(self):
        r = NFSM(".", 1, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("ABC")]], r.chains)

    def test_bracket(self):
        r = NFSM("[AB]", 1, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("AB")]], r.chains)

    def test_inverse_bracket(self):
        r = NFSM("[^A]", 1, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("BC")]], r.chains)

    def test_two_bracket(self):
        r = NFSM("[AB][BC]", 2, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("AB"), set("BC")], r.chains)

class TestOr(TestNFSMBase):
    """Tests involving more than one chain but no quantifiers"""
    def test_or(self):
        r = NFSM("A|C", 1, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A")], r.chains)
        self.assertIn([set("C")], r.chains)
        self.assertEqual(2, len(r.chains))

    def test_twochar_or(self):
        r = NFSM("AB|BC", 2, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("B")], r.chains)
        self.assertIn([set("B"), set("C")], r.chains)
        self.assertEqual(2, len(r.chains))

    def test_three_or(self):
        r = NFSM("AB|BC|AC", 2, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("B")], r.chains)
        self.assertIn([set("B"), set("C")], r.chains)
        self.assertIn([set("A"), set("C")], r.chains)
        self.assertEqual(3, len(r.chains))

    def test_twochar_or_bracket(self):
        r = NFSM("[AB][^A]|[BC][^B]", 2, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("AB"), set("BC")], r.chains)
        self.assertIn([set("BC"), set("AC")], r.chains)
        self.assertEqual(2, len(r.chains))

class TestQuantifiers(TestNFSMBase):
    """Tests involving Quantifiers"""
    def test_one_kleene_star(self):
        r = NFSM("A*", 3, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("A"), set("A"), set("A")]], r.chains)

    def test_two_kleene_star(self):
        r = NFSM("A*B*", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn( [set("A"), set("A"), set("A")], r.chains)
        self.assertIn( [set("A"), set("A"), set("B")], r.chains)
        self.assertIn( [set("A"), set("B"), set("B")], r.chains)
        self.assertIn( [set("B"), set("B"), set("B")], r.chains)
        self.assertEqual(4, len(r.chains))

    def test_one_plus(self):
        r = NFSM("A+", 3, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("A"), set("A"), set("A")]], r.chains)

    def test_plus_and_star(self):
        r = NFSM("A+B*", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn( [set("A"), set("A"), set("A")], r.chains)
        self.assertIn( [set("A"), set("A"), set("B")], r.chains)
        self.assertIn( [set("A"), set("B"), set("B")], r.chains)
        self.assertEqual(3, len(r.chains))

    def test_star_and_plus(self):
        r = NFSM("A*B+", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn( [set("A"), set("A"), set("B")], r.chains)
        self.assertIn( [set("A"), set("B"), set("B")], r.chains)
        self.assertIn( [set("B"), set("B"), set("B")], r.chains)
        self.assertEqual(3, len(r.chains))

    def test_plus_plus(self):
        r = NFSM("A+B+", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn( [set("A"), set("A"), set("B")], r.chains)
        self.assertIn( [set("A"), set("B"), set("B")], r.chains)
        self.assertEqual(2, len(r.chains))

    def test_question(self):
        r = NFSM("A?", 1, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("A")]], r.chains)

    def test_any_question(self):
        r = NFSM(".?", 1, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("ABC")]], r.chains)

    def test_bracket_question(self):
        r = NFSM("[AC]?", 1, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("AC")]], r.chains)

    def test_bracket_star(self):
        r = NFSM("[AC]*", 3, "ABC")
        self.assert_no_references(r)
        self.assertEqual([[set("AC"), set("AC"), set("AC")]], r.chains)

    def test_star_and_question(self):
        r = NFSM("A*B?", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("A"), set("A")], r.chains)
        self.assertIn([set("A"), set("A"), set("B")], r.chains)
        self.assertEqual(2, len(r.chains))
        
    def test_plus_and_question(self):
        r = NFSM("A+B?", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("A"), set("A")], r.chains)
        self.assertIn([set("A"), set("A"), set("B")], r.chains)
        self.assertEqual(2, len(r.chains))

    def test_star_question_star(self):
        r = NFSM("A*B?C*", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("A"), set("A")], r.chains)
        self.assertIn([set("A"), set("A"), set("B")], r.chains)
        self.assertIn([set("A"), set("A"), set("C")], r.chains)
        self.assertIn([set("A"), set("B"), set("C")], r.chains)
        self.assertIn([set("B"), set("C"), set("C")], r.chains)
        self.assertIn([set("A"), set("C"), set("C")], r.chains)
        self.assertIn([set("C"), set("C"), set("C")], r.chains)
        self.assertEqual(7, len(r.chains))

    def test_plus_question_star(self):
        r = NFSM("A+B?C*", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("A"), set("A")], r.chains)
        self.assertIn([set("A"), set("A"), set("B")], r.chains)
        self.assertIn([set("A"), set("A"), set("C")], r.chains)
        self.assertIn([set("A"), set("B"), set("C")], r.chains)
        self.assertIn([set("A"), set("C"), set("C")], r.chains)
        self.assertEqual(5, len(r.chains))

    def test_star_question_plus(self):
        r = NFSM("A*B?C+", 3, "ABC")
        self.assert_no_references(r)
        self.assertIn([set("A"), set("A"), set("C")], r.chains)
        self.assertIn([set("A"), set("B"), set("C")], r.chains)
        self.assertIn([set("B"), set("C"), set("C")], r.chains)
        self.assertIn([set("A"), set("C"), set("C")], r.chains)
        self.assertIn([set("C"), set("C"), set("C")], r.chains)
        self.assertEqual(5, len(r.chains))
        
class TestGroups(TestNFSMBase):
    """This set of tests involves groups and backreferences.
    These tests must not only test that the sets are correct, but that the
    actual set objects are linked appropriately
    
    """

    def test_single_group(self):
        r = NFSM("(A)\\1", 2, "ABC")
        self.assertEqual([[set("A"), set("A")]], r.chains)
        self.assertIs(r.chains[0][0], r.chains[0][1])

    def test_dot_group(self):
        r = NFSM("(.)\\1", 2, "ABC")
        self.assertIn([set("ABC"), set("ABC")], r.chains)
        self.assertEqual(1, len(r.chains))
        for chain in r.chains:
            self.assertIs(chain[0], chain[1])

    def test_group_2nd_pos(self):
        r = NFSM("A(.)B\\1", 4, "ABC")
        self.assertIn([set("A"), set("ABC"), set("B"), set("ABC")], r.chains)
        self.assertEqual(1, len(r.chains))
        self.assertIs(r.chains[0][1], r.chains[0][3])

    def test_two_groups(self):
        r = NFSM("(A)(B)\\2\\1", 4, "ABC")
        self.assertIn([set("A"), set("B"), set("B"), set("A")], r.chains)
        self.assertEqual(1, len(r.chains))
        for chain in r.chains:
            self.assertIs(chain[0], chain[3])
            self.assertIs(chain[1], chain[2])

    def test_two_dot_groups(self):
        r = NFSM("(.)(.)\\2\\1", 4, "ABC")
        self.assertIn([set("ABC"), set("ABC"), set("ABC"), set("ABC")], r.chains)
        self.assertEqual(1, len(r.chains))
        for chain in r.chains:
            self.assertIs(chain[0], chain[3])
            self.assertIs(chain[1], chain[2])

    def test_two_dot_group(self):
        r = NFSM("(..)\\1", 4, "ABC")
        self.assertIn([set("ABC"), set("ABC"), set("ABC"), set("ABC")], r.chains)
        for chain in r.chains:
            self.assertIs(chain[0], chain[2])
            self.assertIs(chain[1], chain[3])

    def test_bracket_group(self):
        r = NFSM("([^C])\\1", 2, "ABC")
        self.assertEqual([[set("AB"), set("AB")]], r.chains)
        self.assertIs(r.chains[0][0], r.chains[0][1])

    def test_var_len_group(self):
        r = NFSM("([^C][^C]?)\\1C*", 4, "ABC")
        self.assertIn([set("AB"), set("AB"), set("AB"), set("AB")], r.chains)
        self.assertIn([set("AB"), set("AB"), set("C"), set("C")], r.chains)
        for chain in r.chains:
            if chain[-1] == set("C"):
                self.assertIs(chain[0], chain[1])
            else:
                self.assertIs(chain[0], chain[2])
                self.assertIs(chain[1], chain[3])


class TestMatching(TestNFSMBase):
    """Test some more complex regexes without and with constraints

    """
    def test_simple(self):
        r = NFSM("ABC", 3, "ABC")
        self.assert_no_references(r)
        self.assertTrue(r.match("ABC"))
        self.assertFalse(r.match("CBA"))
        self.assertFalse(r.match("ABCD"))
        self.assertFalse(r.match("AABC"))

    def test_complex(self):
        r = NFSM("F.*[AO].*[AO].*", 9, string.ascii_uppercase)
        self.assert_no_references(r)
        # A few positive matches
        self.assertTrue(r.match("FBCODEAFG"))
        self.assertTrue(r.match("FBOCDEAFG"))
        self.assertTrue(r.match("FBCADEAFG"))
        self.assertTrue(r.match("FBCADEFOG"))
        self.assertTrue(r.match("FODEFOGHI"))
        self.assertTrue(r.match("FBCAAEFOG"))
        self.assertTrue(r.match("FBCAOEFHG"))

        # A few negative matches
        self.assertFalse(r.match("ABCODEAFG"))
        self.assertFalse(r.match("FBZCDEAFG"))
        self.assertFalse(r.match("FBCABEZFG"))
        self.assertFalse(r.match("FZZZZZZZZ"))

        r.constrain_slot(1, set("AO"))
        
        self.assertFalse(r.match("FBCODEAFG"))
        self.assertFalse(r.match("FBOCDEAFG"))
        self.assertFalse(r.match("FBCADEAFG"))
        self.assertFalse(r.match("FBCADEFOG"))
        self.assertTrue(r.match("FODEFOGHI"))
        self.assertFalse(r.match("FBCAAEFOG"))
        self.assertFalse(r.match("FBCAOEFHG"))

        self.assertFalse(r.match("ABCODEAFG"))
        self.assertFalse(r.match("FBZCDEAFG"))
        self.assertFalse(r.match("FBCAOEZFG"))
        self.assertFalse(r.match("FZZZZZZZZ"))

    def test_multi_or(self):
        r = NFSM("(DI|NS|TH|OM)*", 8, string.ascii_uppercase)
        self.assert_no_references(r)

        self.assertTrue(r.match("DIDIDIDI"))
        self.assertTrue(r.match("DINSTHOM"))
        self.assertTrue(r.match("OMTHNSDI"))

        self.assertFalse(r.match("ADINSTHOZ"))
        self.assertFalse(r.match("ZZZZZZZZ"))

        r.constrain_slot(0, set("DZ"))

        self.assertTrue(r.match("DIDIDIDI"))
        self.assertTrue(r.match("DINSTHOM"))
        self.assertFalse(r.match("OMTHNSDI"))
        self.assertFalse(r.match("ZINSTHOM"))

    def test_or_star(self):
        r = NFSM("(RR|HHH)*.?", 10, string.ascii_uppercase)
        self.assert_no_references(r)

        self.assertTrue(r.match("RRRRRRRRRR"))
        self.assertTrue(r.match("RRRRRRHHHA"))
        self.assertTrue(r.match("RRRRRRHHHR"))
        self.assertTrue(r.match("RRRRRRHHHH"))
        self.assertTrue(r.match("HHHHHHRRRR"))
        self.assertTrue(r.match("RRHHHRRHHH"))
        self.assertTrue(r.match("HHHRRRRRRZ"))

        self.assertFalse(r.match("RHHHHHHHHH"))
        self.assertFalse(r.match("HHHRRRRRR"))
        self.assertFalse(r.match("HHHHHHHHHRR"))
        self.assertFalse(r.match("HHRRRRRRRR"))
        self.assertFalse(r.match("RRRRRRRRRRZ"))
        self.assertFalse(r.match("RRRRRRRRRRH"))

        r.constrain_slot(2, set("H"))

        self.assertTrue(r.match("RRHHHHHHRR"))
        self.assertTrue(r.match("HHHRRRRHHH"))
        self.assertTrue(r.match("HHHHHHHHHZ"))
        self.assertFalse(r.match("RRRRHHHHHH"))
        self.assertFalse(r.match("RRRRRRHHHZ"))

        r.constrain_slot(2, set("R"))

        self.assertFalse(r.match("HHHHHHHHHZ"))
        self.assertFalse(r.match("RRRRHHHHHH"))
        self.assertFalse(r.match("RRRRRRHHHH"))
        self.assertFalse(r.match("HHHHHHRRRR"))

    def test_simple_constraints(self):
        r = NFSM("...", 3, "ABC")
        self.assert_no_references(r)

        self.assertTrue(r.match("AAA"))
        self.assertTrue(r.match("ABC"))

        r.constrain_slot(1, set("AB"))
        self.assertTrue(r.match("AAA"))
        self.assertTrue(r.match("CBC"))
        self.assertFalse(r.match("ACA"))
        self.assertFalse(r.match("BCA"))

        r.constrain_slot(0, set("C"))
        self.assertTrue(r.match("CAB"))
        self.assertFalse(r.match("BAB"))

    def test_backref_simple(self):
        r = NFSM("(.)\\1", 2, "ABC")
        self.assertTrue(r.match("AA"))
        self.assertTrue(r.match("CC"))
        self.assertFalse(r.match("AB"))

        r.constrain_slot(0, set("AB"))

        self.assertTrue(r.match("AA"))
        self.assertTrue(r.match("BB"))
        self.assertFalse(r.match("CC"))

        r.constrain_slot(1, set("BC"))

        self.assertTrue(r.match("BB"))
        self.assertFalse(r.match("AA"))
        self.assertFalse(r.match("CC"))

class TestPeek(TestNFSMBase):
    def test_simple_peek(self):
        r = NFSM("[ABC][AB]", 2, "ABC")
        self.assert_no_references(r)

        self.assertEqual(set("ABC"), r.peek_slot(0))
        self.assertEqual(set("AB"), r.peek_slot(1))

    def test_or_peek_and_constraint(self):
        r = NFSM("AB|BC", 2, "ABC")
        self.assert_no_references(r)

        self.assertEqual(set("AB"), r.peek_slot(0))
        self.assertEqual(set("BC"), r.peek_slot(1))

        r.constrain_slot(0, set("AC"))

        self.assertEqual(set("A"), r.peek_slot(0))
        self.assertEqual(set("B"), r.peek_slot(1))

class TestRealRegexType(type):
    def __init__(cls, *args, **kwargs):
        super(TestRealRegexType, cls).__init__(*args, **kwargs)

        # Create the test methods from the defined regexes
        for i, regex in enumerate(cls.regexes):
            setattr(cls, "test_{0}".format(i),
                    lambda self: self._compare(regex[0], regex[1], regex[2])
                    )
            setattr(getattr(cls, "test_{0}".format(i)), "__doc__",
                    regex[0]
                    )
class TestRealRegex(TestNFSMBase, metaclass=TestRealRegexType):
    regexes = [
            ("(DI|NS|TH|OM)*", 4, "DINSTHOMZ")
            ]

    def _compare(self, regex_str, length, alphabet):
        myr = NFSM(regex_str, length, alphabet)
        realr = re.compile(regex_str+"$")

        for s in ("".join(x) for x in product(alphabet, repeat=length)):
            self.assertEqual(bool(realr.match(s)), myr.match(s), msg=s)


if __name__ == "__main__":
    unittest.main()
