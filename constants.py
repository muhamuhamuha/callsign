import inspect
from enum import Enum
from inspect import _empty as Empty


# creating an enumeration from standard library's inspect._ParameterKind
# with the addition of "VULNERABLE_DEFAULT"
_kinds = [pk.name for pk in inspect._ParameterKind] + ['VULNERABLE_DEFAULT']

ParamKinds = Enum('ParamKinds', [tuple([kind]*2) for kind in _kinds], type=str)
ParamKinds.__doc__ = f"""
    An enumeration created from the standard library's _ParameterKind enum:
    {_kinds[:-1]} (found in the standard library's inspect module)
    with a single addition: the VULNERABLE_DEFAULT.

    VULNERABLE_DEFAULT is interchangeable with POSITIONAL_OR_KEYWORD, except
    that its a parameter that was given a default value, and that default
    has been unintentionally overridden by a VARARGS parameter, e.g.:

    >>> def hello(y=10, *args): return y, args
    >>> print( hello() )
    (10, ())
    >>> print( hello(1, 2, 3) )
    (1, (2, 3))  # note, y = 10 was overridden, y is now 1
"""


