# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from random import random, randint as _randint
from os.path import split, realpath, abspath
import sys

from wxgeometrie.param import tolerance as EPSILON

_module_path = split(realpath(sys._getframe().f_code.co_filename))[0]
ROOTDIR = abspath(_module_path + '/..') # /.../nom_du_projet/
WXGEODIR = ROOTDIR + '/wxgeometrie'

def randint(a, b = None):
    if b is None:
        b = a
        a = 0
    return _randint(a, b)

def rand():
    return randint(50) - randint(50) + random()

def assertAlmostEqual(x, y):
    if type(x) == type(y) and isinstance(x, (tuple, list)):
        for x_elt, y_elt in zip(x, y):
            assertAlmostEqual(x_elt, y_elt)
    else:
        TEST = abs(y - x) < EPSILON
        if not TEST:
            print x,  "!=",  y
        assert TEST

def assertNotAlmostEqual(x, y):
    # TODO: define test for tuple
    TEST = abs(y - x) > EPSILON
    if not TEST:
        print x,  "==",  y
    assert TEST

def assertEqual(x, y):
    if x != y:
        print('''
--------------
 *** FAIL ***
-> Output:
%s
-> Expected:
%s
--------------
''' %(repr(x), repr(y)))
    assert (x == y)

assertEq = assertEqual

def assertRaises(error, f, *args, **kw):
    try:
        f(*args, **kw)
    except Exception as e:
        assert type(e) == error
    else:
        raise AssertionError, '%s should be raised.' %type(e).__name__
