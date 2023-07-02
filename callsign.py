"""
>>> import callsign
>>> def f(x, y):
...     return x, y
>>> params = callsign(f, 'hi', y=2)
>>> params
{
    'x': Paramattrs(name='x',
                    value='hi',
                    default=inspect._empty,
                    kind=ParamKinds.POSITIONAL_OR_KEYWORD,
                    defaulted=False,
                    annotation=inspect._empty),
    'y': Paramattrs(name='y',
                    value=2,
                    default=inspect._empty,
                    kind=ParamKinds.POSITIONAL_OR_KEYWORD,
                    defaulted=False,
                    annotation=inspect._empty),
}
>>> params['x'].value
'hi'
>>> params['x'].annotation
inspect._empty
>>> callsign.isempty(params['x'].annotation)
True
"""

import inspect
import sys
from enum import Enum

from types import ModuleType
from typing import (
    Any,
    Callable,
    NamedTuple,
    ParamSpec,
)

_P = ParamSpec('P')

# creating an Enum from standard library's inspect._ParameterKind
# with the addition of "VULNERABLE_DEFAULT"
_kinds = [pk.name for pk in inspect._ParameterKind] + ['VULNERABLE_DEFAULT']

ParamKinds = Enum('ParamKinds', [tuple([kind]*2) for kind in _kinds], type=str)
ParamKinds.__doc__ = f"""
    An enumeration created from the standard library's _ParameterKind enum:
    {_kinds[:-1]} (found in the standard library's inspect module)
    with a single addition: the VULNERABLE_DEFAULT.

    VULNERABLE_DEFAULT is interchangeable with POSITIONAL_OR_KEYWORD; but also,
    it is a parameter that was given a default value, and that default
    has been overridden by a VARARGS parameter, e.g.:

    >>> def hello(x=10, *args): return x, args
    >>> print( hello() )
    (10, ())
    >>> print( hello(1, 2, 3) )
    (1, (2, 3))  # x = 10 was overridden, x is now 1
"""


class Paramattrs(NamedTuple):
    """
    A collection of the parameter's attributes:
    +------------+----------------+-------------------------------------------+
    | Attribute  | Type           | Value                                     |
    +============+================+===========================================+
    | name       | str            | The parameter name                        |
    +------------+----------------+-------------------------------------------+
    | value      | Any            | The parameter's value; NOTE this could be |
    |            |                | the parameter's default value (in which   |
    |            |                | case, the Attribute passed will be False) |
    +------------+----------------+-------------------------------------------+
    | default    | Any or         | If a default value was given, it will be  |
    |            | inspect._empty | assigned here; otherwise it's             |
    |            |                | inspect._empty                            |
    +------------+----------------+-------------------------------------------+
    | kind       | Any            | One of ParamKinds enumeration:            |
    |            |                |   - VAR_POSITIONAL                        |
    |            |                |   - VAR_KEYWORD                           |
    |            |                |   - POSITIONAL_OR_KEYWORD                 |
    |            |                |   - POSITIONAL_ONLY                       |
    |            |                |   - KEYWORD_ONLY                          |
    |            |                |   - VULNERABLE_DEFAULT                    |
    +------------+----------------+-------------------------------------------+
    | defaulted  | bool           | Flag that is False if a value was passed  |
    |            |                | to the parameter, and True if no value    |
    |            |                | was given (in which case the default is   |
    |            |                | being used)                               |
    +------------+----------------+-------------------------------------------+
    | annotation | type or        | If the function's parameters have type    |
    |            | inspect._empty | hints they are included here; otherwise   |
    |            |                | it's inspect._empty                       |
    +------------+----------------+-------------------------------------------+
    """
    name: str
    value: Any
    default: Any | inspect._empty
    kind: ParamKinds
    defaulted: bool
    annotation: Callable | inspect._empty

    @classmethod
    def from_sig_metadata(cls,
                          param: inspect.Parameter,
                          bargs: inspect.BoundArguments,
                          kinds: set[ParamKinds]):

        value = bargs.arguments.get(param.name, param.default)

        kind = ParamKinds(param.kind.name)
        hint = param.annotation or inspect._empty
        dftd = bargs.arguments.get(param.name, inspect._empty) is inspect._empty

        if (ParamKinds.VAR_POSITIONAL in kinds
            and kind is ParamKinds.POSITIONAL_OR_KEYWORD
            and value not in (param.default, inspect._empty)):
            kind = ParamKinds.VULNERABLE_DEFAULT

        return cls(param.name, value, param.default, kind, dftd, hint)


class CallSign(ModuleType):

    def __init__(self):
        super().__init__(__name__)
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self,
                 fn: Callable[_P, Any],
                 *args: _P.args,
                 **kwargs: _P.kwargs,
                 ) -> dict[str, Paramattrs]:

        sig = inspect.signature(fn)
        # don't use bargs.apply_defaults, we will apply manually
        bargs = sig.bind(*args, **kwargs)
        kinds = {param.kind.name for param in sig.parameters.values()}

        return {pname: Paramattrs.from_sig_metadata(param, bargs, kinds)
                for pname, param in sig.parameters.items()}

    @staticmethod
    def isempty(whatever: Any) -> bool:
        """
        >>> import inspect, callsign
        >>> callsign.isempty(inspect._empty)
        True
        """
        return whatever is inspect._empty


sys.modules[__name__] = CallSign()

