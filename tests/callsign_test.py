import pytest

import inspect

import callsign
from callsign import ParamKinds

from typing import (
    Any,
    Callable,
    NamedTuple,
    Optional,
)


@pytest.mark.parametrize('sig, positionals, keywords, expected_defaults', [
 # base case
 ('a, b=2', (1,), {}, ['b']),
 # does it work with positional only
 ('a, /, b=2', (1,), {}, ['b']),
 # does it really work with positional only
 ('a=2, b=2, /', (), {}, ['a', 'b']),
 # does it work with varargs
 ('a=2, *args', (), {}, ['a']),
 # does it work with keyword-only defaults
 ('*, a=2', (), {}, ['a']),
 # what if we override the default
 ('a=2', (3,), {}, []),
 # override with kwarg?
 ('a=2', (), {'a': 3}, []),
])
def test_callsign_defaulted(sig: str,
                            positionals: tuple,
                            keywords: dict,
                            expected_defaults: list[str],
                            FUNCC_MAKER: pytest.fixture):
    params = callsign(FUNCC_MAKER, *positionals, **keywords)
    for default_param_name in expected_defaults:
        assert params.get(default_param_name).defaulted

@pytest.mark.parametrize('sig, positionals, keywords', [
 # one parameter
 ('a', (1,), {}),
 # multiple positional parameters
 ('a, b', (1,), {'b': 2}),
 # annotation
 ('a, b: int', (1,), {'b': 2}),
 # default param
 ('a, b: int = 2, c: float = 2.3', (1,), {'b': 3}),
 # positional-only param
 ('a, /, b: int', (1, 2), {}),
 # keyword-only param
 ('a, b: int = 2, *, c: bool = True', (1,), {'c': False}),
 # varargs
 ('*args', ('a', 'b', 'c', 1, 2, 3, False), {}),
 # varkwargs
 ('**kwargs', (), {'greeting': 'hello', 'farewell': 'bye'}),
 # args & kwargs
 ('*args, **kwargs', (1, 2), {'a': 'b'}),
 # all together now
 ('a, /, b, c: int = 2, *args, _d: bool = True, **kwargs',
  (1, 2, 'overrode default c', 'extra-arg1', 'extra2'),
  {'greeting': ['hello', 'moshimoshi'], 'farewell': ['goodbye', 'sayonara']}),
])
def test_callsign_values(sig: str,
                         positionals: tuple,
                         keywords: dict,
                         FUNCC_MAKER: pytest.fixture):

    # compile a list of expected values from given positionals & keywords
    expected_values = list(positionals) + list(keywords.values())

    params = callsign(FUNCC_MAKER, *positionals, **keywords)

    test_values = []
    for pattrs in params.values():
        # defaulted, meaning user did not pass a value and the default is used
        if pattrs.defaulted:
            continue
        # extend test_values with the tuple without wrapping it in a list
        elif pattrs.kind == 'VAR_POSITIONAL':
            test_values += pattrs.value
        # for testing purposes, so that it matches with expected_values
        # keyword.values(), we will extend the list with kwarg values
        elif pattrs.kind == 'VAR_KEYWORD':
            test_values += pattrs.value.values()
        else:
            test_values += [pattrs.value]

    print(f'\nexpected_values: {expected_values}\ntest_values: {test_values}')
    assert test_values == expected_values


class VDefaultExp(NamedTuple):
    """Expected"""
    vparam: str  # name of vulnerable default param
    vvalue: Any  # vulnerable default param's value
    varargs: tuple  # varargs value(s)


@pytest.mark.parametrize('sig, positionals, keywords, expected', [
 ('a=2, *args', (1, 2, 3), {}, VDefaultExp('a', 1, (2, 3))),

])
def test_callsign_vulnerable_default(sig: str,
                                     positionals: tuple,
                                     keywords: dict,
                                     expected: VDefaultExp,
                                     FUNCC_MAKER: pytest.fixture):

    params = callsign(FUNCC_MAKER, *positionals, **keywords)
    assert params[expected.vparam].kind is ParamKinds.VULNERABLE_DEFAULT
    assert params[expected.vparam].value == expected.vvalue
    assert params['args'].value == expected.varargs


@pytest.mark.parametrize('whatever, expected', [
 (inspect._empty, True),
 ('hello', False),
 (False, False),
 (None, False),
 (0, False),
 (1, False),
 (1.5, False),
 ('', False),
])
def test_is_paramattr_empty(whatever: Any, expected: bool):
    assert callsign.isempty(whatever) is expected

