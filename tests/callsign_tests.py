import pytest
import unittest.mock as mock

import re
import ast
import inspect

from typing import (
    Any,
    Callable,
    Optional,
)

import callsign
from callsign import Paramattr
from constants import ParamKinds


def _create_return_params_from_sig(sig: str, decl: str) -> Callable:
    parsed = ast.parse(decl).body[0].args

    param_order = ['posonlyargs', 'args', 'vararg', 'kwonlyargs', 'kwarg']

    params = []
    for param_type in param_order:
        parsed_paramtype = getattr(parsed, param_type, None)
        if isinstance(parsed_paramtype, (list, tuple, set)):
            params += [a.arg for a in parsed_paramtype]
        elif parsed_paramtype is None:
            pass
        else:
            params += [parsed_paramtype.arg]

    return ', '.join(params)


@pytest.mark.parametrize(
    'sig, expected', [
        # one parameter
        ('a', 'a'),
        # multiple positional parameters
        ('a, b', 'a, b'),
        # annotation
        ('a, b: int', 'a, b'),
        # default param
        ('a, b: int = 2', 'a, b'),
        # positional-only param
        ('a, /, b: int', 'a, b'),
        # keyword-only param
        ('a, b: int = 2, *, c: bool = True', 'a, b, c'),
        # varargs
        ('*args', 'args'),
        # varkwargs
        ('**kwargs', 'kwargs'),
        # args & kwargs
        ('*args, **kwargs', 'args, kwargs'),
        # all together now
        (
            'a, /, b, c: int = 2, *args, _d: bool = True, **kwargs',
            'a, b, c, args, _d, kwargs'
        ),
    ]
)
def test_create_return_params_from_sig(sig: str,
                                       expected: str,
                                       FUNCC_DECLARATION: pytest.fixture):
    decl = FUNCC_DECLARATION.format(sig=sig)
    params = _create_return_params_from_sig(sig, decl)
    assert params == expected


@pytest.fixture(scope='function')
def FUNCC_MAKER(sig: str, FUNCC_DECLARATION: pytest.fixture) -> Callable:
    """
    NOTE fixture created automatically when sig passed by parametrization.
    For this to work, sig must be passed named as 'sig' exactly, e.g.:

    ```
    @pytest.mark.parametrize('sig', ('a', 'b'))
    def test_something(sig, FUNCC_MAKER):
        # FUNCC_MAKER already initialized with 'a' on 1st run, then 'b'
        assert FUNCC_MAKER.__name__ == 'funcc'
    ```
    """
    decl = FUNCC_DECLARATION.format(sig=sig)
    return_params = _create_return_params_from_sig(sig, decl)
    exec(decl + ' ' + return_params)
    return locals()['FUNCC']


@pytest.mark.parametrize(
    'sig, positionals, keywords, defaulted_params', [
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
    ]
)
def test_callsign_defaulted(sig: str,
                            positionals: tuple,
                            keywords: dict,
                            defaulted_params: list[str],
                            FUNCC_MAKER: pytest.fixture):
    params = callsign(FUNCC_MAKER, *positionals, **keywords)
    for default_param_name in defaulted_params:
        assert params.get(default_param_name).defaulted


@pytest.mark.parametrize(
    'sig, positionals, keywords', [
        # one parameter
        ('a', (1,), {}),
        ## multiple positional parameters
        ('a, b', (1,), {'b': 2}),
        ## annotation
        ('a, b: int', (1,), {'b': 2}),
        ## default param
        ('a, b: int = 2, c: float = 2.3', (1,), {'b': 3}),
        ## positional-only param
        ('a, /, b: int', (1, 2), {}),
        ## keyword-only param
        ('a, b: int = 2, *, c: bool = True', (1,), {'c': False}),
        # varargs
        ('*args', ('a', 'b', 'c', 1, 2, 3, False), {}),
        # varkwargs
        ('**kwargs', (), {'greeting': 'hello', 'farewell': 'bye'}),
        # args & kwargs
        ('*args, **kwargs', (1, 2), {'a': 'b'}),
        # all together now
        (
            'a, /, b, c: int = 2, *args, _d: bool = True, **kwargs',
            (1, 2, 'overrode default c', 'extra-arg1', 'extra2'),
            {
                'greeting': ['hello', 'moshimoshi'],
                'farewell': ['goodbye', 'sayonara'],
            },
        ),
    ]
)
def test_callsign_values(sig: str,
                         positionals: tuple,
                         keywords: dict,
                         FUNCC_MAKER: pytest.fixture):

    # compile a list of expected values from given positionals & keywords
    expected_values = list(positionals) + list(keywords.values())

    params = callsign(FUNCC_MAKER, *positionals, **keywords)

    test_values = []
    for pattr in params.values():
        # defaulted, meaning user did not pass a value and the default is
        # being used
        if pattr.defaulted:
            continue
        # extend test_values with the tuple without wrapping it in a list
        elif pattr.kind == 'VAR_POSITIONAL':
            test_values += pattr.value
        # for testing purposes, so that it matches with expected_values
        # keyword.values(), we will extend the list with kwarg values
        elif pattr.kind == 'VAR_KEYWORD':
            test_values += pattr.value.values()
        else:
            test_values += [pattr.value]

    print(f'\nexpected_values: {expected_values}\ntest_values: {test_values}')
    assert test_values == expected_values


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
def test_is_paramattr_empty(whatever: Any, expected: bool):
    assert callsign.is_paramattr_empty(whatever) is expected

