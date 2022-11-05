import pytest
import unittest.mock as mock

import inspect

import callsign
from callsign import Paramattr
from constants import ParamKinds


@pytest.fixture
def FUNC_MAKER() -> callable:
    pass


@pytest.mark.parametrize(
    'whatever, expected', [
        (inspect._empty, True),
        ('hello', False),
        (False, False),
        (None, False),
        (0, False),
        (1, False),
        (1.5, False),
        ('', False),
    ]
)
def test_is_paramattr_empty(whatever, expected):
    assert callsign.is_paramattr_empty(whatever) is expected


#@pytest.mark.parametrize(
#    'fn, _args, _kwargs, expected', [
#        (
#            lambda x, y: (x, y),
#            ('hello'),
#            {'y': 1},
#            {'x': Paramattr('x', 'hello', ),
#             'y': Paramattr('y', 1, Pa)},
#
#        ),
#    ]
#)
#def test_callsign(fn: callable, _args: list, _kwargs: dict, expected: dict):
#    params = callsign(fn, *_args, **_kwargs)
#    breakpoint()
#    assert computed == expected

