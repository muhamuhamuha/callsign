import pytest

import ast

from typing import Callable

def _create_return_params_from_sig(sig: str, decl: str) -> str:
    """Creates a string of param names from a given function signature.

    >>> def hello(x): pass
    >>> _create_return_params_from_sig(hello)
    'x'
    >>> def hello(x, y): pass
    >>> _create_return_params_from_sig(hello)
    'x, y'
    >>> def hello(x, y: int = 2): pass
    >>> _create_return_params_from_sig(hello)
    'x, y'
    >>> def hello(a, /, b, c: int = 2, *args, _d: bool = True, **kwargs): pass
    >>> _create_return_params_from_sig(hello)
    'a, b, c, args, _d, kwargs'
    """
    parsed = ast.parse(decl).body[0].args
    param_order = ['posonlyargs', 'args', 'vararg', 'kwonlyargs', 'kwarg']

    params = []
    for param_type in param_order:
        parsed_paramtype = getattr(parsed, param_type, None)
        if parsed_paramtype is None:
            continue
        elif isinstance(parsed_paramtype, (list, tuple, set)):
            params += [a.arg for a in parsed_paramtype]
        else:
            params += [parsed_paramtype.arg]

    return ', '.join(params)


@pytest.fixture
def FUNCC_DECLARATION(sig: str) -> str:
    """
    FUNCC: a very functional func (inspired by the vernacular "thicc")
    """
    return f'def FUNCC({sig}): return'


@pytest.fixture
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

