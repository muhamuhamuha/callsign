import pytest
import inspect
import callsign


def test_positional_only():
    def positional_only(x):
        pass

    params = callsign(positional_only, 1)
    result = callsign.arguments(params)
    assert result == {'x': 1}


def test_positional_or_keyword():
    def positional_or_keyword(x=10):
        pass

    params = callsign(positional_or_keyword, 5)
    result = callsign.arguments(params)
    assert result == {'x': 5}

    params = callsign(positional_or_keyword)
    result = callsign.arguments(params)
    assert result == {'x': 10}

def test_keyword_only():
    def keyword_only(*, x):
        pass

    params = callsign(keyword_only, x=20)
    result = callsign.arguments(params)
    assert result == {'x': 20}

def test_var_positional():
    def var_positional(*args):
        pass

    params = callsign(var_positional, 1, 2, 3)
    result = callsign.arguments(params)
    assert result == {'args': (1, 2, 3)}

def test_var_keyword():
    def var_keyword(**kwargs):
        pass

    params = callsign(var_keyword, x=1, y=2)
    result = callsign.arguments(params)
    assert result == {'kwargs': {'x': 1, 'y': 2}}

def test_all_kinds():
    def all_kinds(x, /, y, *args, z, **kwargs):
        pass

    params = callsign(all_kinds, 1, 2, 3, z=4, k=5)
    result = callsign.arguments(params)
    assert result == {
        'x': 1,
        'y': 2,
        'args': (3,),
        'z': 4,
        'kwargs': {'k': 5}
    }

def test_callsign_arguments_with_mutators():
    def positional_or_keyword(x=10):
        pass

    params = callsign(positional_or_keyword, 5)
    result = callsign.arguments(params, mutators={'x': 15})
    assert result == {'x': 15}


def test_callsign_arguments_safe_mode():
    def all_kinds(x, /, y, *args, z, **kwargs):
        pass

    params = callsign(all_kinds, 1, 2, 3, z=4, k=5)
    result = callsign.arguments(params, safe=True)
    assert result == ((1,), {'y': 2, 'args': (3,), 'z': 4, 'kwargs': {'k': 5}})

