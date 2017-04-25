from __future__ import print_function
import unittest
from cmsl1t.utils.timers import timerfunc, timerfunc_log_to


def simple_logger(*args):
    print(args)


@timerfunc
def wrapping_method():
    pass


@timerfunc_log_to(simple_logger)
def wrapping_method_with_logger():
    pass


class TestTimerfunc(unittest.TestCase):

    def test_wrapping(self):
        wrapped = getattr(wrapping_method, "__wrapped__")
        self.assertEqual(wrapped.__name__, 'wrapping_method')

    def test_wrapping_withlogger(self):
        wrapped = getattr(wrapping_method_with_logger, "__wrapped__")
        self.assertEqual(wrapped.__name__, 'wrapping_method_with_logger')
