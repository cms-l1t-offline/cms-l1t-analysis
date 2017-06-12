from __future__ import print_function
from nose.tools import assert_equal
import numpy as np
from cmsl1t.recalc.jet_matching import jet_match


class Jet():
    def __init__(self, eta, phi):
        self.eta = eta
        self.phi = phi


jetlist_1 = [Jet(0, 0), Jet(2, 1.3)]
jetlist_2 = [Jet(2.3, 1.3), Jet(0.1, 0)]
jetlist_3 = jetlist_1 + [Jet(4, 3)]


def test_jet_match_self():
    matches = jet_match(jetlist_1, jetlist_1)
    assert_equal(np.array(matches).shape, (len(jetlist_1), len(jetlist_1)))
    assert_equal(set(matches), set([(i, i) for i in range(len(jetlist_1))]))


def test_jet_match_similar():
    matches = jet_match(jetlist_1, jetlist_2)
    assert_equal(set(matches), set([(0, 1), (1, 0)]))


def test_jet_match_different():
    matches = jet_match(jetlist_1, jetlist_3)
    assert_equal(len(matches), len(jetlist_1))
