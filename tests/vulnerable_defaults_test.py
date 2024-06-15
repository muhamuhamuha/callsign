import inspect
import pytest

import callsign


def test_vulnerable_default_position():
    def example_function(x=10, *args):
        return x, args

    params = callsign(example_function, 1, 2, 3)
    assert 'x' in params
    assert params['x'].kind == callsign.ParamKinds.VULNERABLE_DEFAULT
    assert params['x'].arg == 1
    assert params['x'].default == 10
    assert params['x'].defaulted == False


def test_vulnerable_default_not_applied():
    def example_function(x=10, *args):
        return x, args

    params = callsign(example_function, 10)
    assert 'x' in params
    assert params['x'].kind == callsign.ParamKinds.POSITIONAL_OR_KEYWORD
    assert params['x'].arg == 10
    assert params['x'].default == 10
    assert params['x'].defaulted == False


def test_vulnerable_default_with_no_varargs():
    def example_function(x=10, y=20):
        return x, y

    params = callsign(example_function, 5, 15)
    assert 'x' in params
    assert params['x'].kind == callsign.ParamKinds.POSITIONAL_OR_KEYWORD
    assert params['x'].arg == 5
    assert params['x'].default == 10
    assert params['x'].defaulted == False


def test_vulnerable_default_with_varargs():
    def example_function(x=10, y=20, *args):
        return x, y, args

    params = callsign(example_function, 5, 15, 25, 30)
    assert 'x' in params
    assert params['x'].kind == callsign.ParamKinds.VULNERABLE_DEFAULT
    assert params['x'].arg == 5
    assert params['x'].default == 10
    assert params['x'].defaulted == False

    assert 'y' in params
    assert params['y'].kind == callsign.ParamKinds.VULNERABLE_DEFAULT
    assert params['y'].arg == 15
    assert params['y'].default == 20
    assert params['y'].defaulted == False


def test_vulnerable_default_keyword():
    def example_function(x=10, *args, y=20):
        return x, y, args

    params = callsign(example_function, y=15)
    assert 'y' in params
    assert params['y'].kind == callsign.ParamKinds.KEYWORD_ONLY
    assert params['y'].arg == 15
    assert params['y'].default == 20
    assert params['y'].defaulted == False

