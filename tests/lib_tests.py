import pytest

import inspect
from functools import wraps

from typing import Callable

import lib


def get_parameter_names(f: Callable[..., None]) -> Callable[..., list[str]]:
    @wraps(f)
    def param_names_getter(*args, **kwargs):
        sig = inspect.signature(f)
        return [*sig.parameters.keys()]
    return param_names_getter


@pytest.mark.parametrize(
    'func, _args, _kwargs, expected_names', [
        (lambda x, y: None, ('hi', 'there'), {}, ['x', 'y']),
    ]
)
def test_get_parameter_names(func, _args, _kwargs, expected_names):
    namer = get_parameter_names(func)
    names = namer(*_args, **_kwargs)
    assert names == expected_names


@pytest.fixture
def MOCK_FUNC(signature: str):
    pass


@pytest.mark.parametrize(
    'f, _args, _kwargs', [
        (lambda x, y, z=None: (x, y, z), (1, 2), {'z': 3},),
    ]
)
def test_create_paramattrs(f, _args, _kwargs):
    sig = inspect.signature(f)
    bargs = sig.bind_partial(*_args, **_kwargs)
    bargs.apply_defaults()

    paramattrs = lib.create_paramattrs(bargs, sig.parameters)
    breakpoint()
    assert 1


