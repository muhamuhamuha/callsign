import inspect
import sys
from enum import Enum

from types import ModuleType
from typing import (
    Any,
    Callable,
    NamedTuple,
    Optional,
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
    | arg        | Any            | The given argument; NOTE this could be    |
    |            |                | the parameter's default value (in which   |
    |            |                | case, defaulted  will be True)            |
    +------------+----------------+-------------------------------------------+
    | default    | Any or         | If a default value was given, it will be  |
    |            | inspect._empty | assigned here; otherwise it's             |
    |            |                | inspect._empty                            |
    +------------+----------------+-------------------------------------------+
    | kind       | ParamKinds     | One of ParamKinds Enum:                   |
    |            |                |   - VAR_POSITIONAL                        |
    |            |                |   - VAR_KEYWORD                           |
    |            |                |   - POSITIONAL_OR_KEYWORD                 |
    |            |                |   - POSITIONAL_ONLY                       |
    |            |                |   - KEYWORD_ONLY                          |
    |            |                |   - VULNERABLE_DEFAULT                    |
    +------------+----------------+-------------------------------------------+
    | defaulted  | bool           | Flag that is `False` if an argument was   |
    |            |                | passed to the parameter, and `True` if    |
    |            |                | the default is being used                 |
    +------------+----------------+-------------------------------------------+
    | annotation | type or        | If the function's parameters have type    |
    |            | inspect._empty | hints, they are included here; otherwise  |
    |            |                | it's inspect._empty                       |
    +------------+----------------+-------------------------------------------+
    """
    name: str
    arg: Any
    default: Any | inspect._empty
    kind: ParamKinds
    defaulted: bool
    annotation: Callable | inspect._empty

    @classmethod
    def from_sig_metadata(
        cls,
        param: inspect.Parameter,
        bargs: inspect.BoundArguments,
        kinds: set[ParamKinds]
    ):

        arg = bargs.arguments.get(param.name, param.default)

        kind = ParamKinds(param.kind.name)
        hint = param.annotation or inspect._empty
        dftd = bargs.arguments.get(param.name, inspect._empty) is inspect._empty

        # re-assign vulnerable default kind
        if (ParamKinds.VAR_POSITIONAL in kinds
            and kind is ParamKinds.POSITIONAL_OR_KEYWORD
            and arg not in (param.default, inspect._empty)):
            kind = ParamKinds.VULNERABLE_DEFAULT

        return cls(param.name, arg, param.default, kind, dftd, hint)


def isempty(whatever: Any) -> bool:
    """
    >>> import inspect, callsign
    >>> callsign.isempty(inspect._empty)
    True
    """
    return whatever is inspect._empty


def arguments(
    params: dict[str, Paramattrs],
    mutators: Optional[dict[str, Any]] = None,
    safe: bool = False,
) ->  dict[str, Any] | tuple[tuple, dict]:
    """
    Strips out all the Paramattrs metadata from a params mapping, leaving only
    the param name mapped to its arg.

    >>> def f(x, /, y: int, *, z: bool = 3): pass
    >>> params = callsign(f, 1, 2, z=3)
    >>> params
    {'x': Paramattrs(name='x',
                     arg=1,
                     default=inspect._empty,
                     kind=ParamKinds.POSITIONAL_ONLY,
                     defaulted=False,
                     annotation=inspect._empty),
     'y': Paramattrs(...),
     'z': Paramattrs(...),}
    >>> callsign.arguments(params)
    {'x': 1, 'y': 2, 'z': 3}
    >>> callsign.arguments(params, mutators={'x': 'hello'})
    {'x': 'hello', 'y': 2, 'z': 3}
    >>> callsign.arguments(params, {'x': 'hello', 'z': 'there'})
    {'x': 'hello', 'y': 2, 'z': 'there'}
    >>> callsign.arguments(params, safe=True)
    (1,), {'y': 2, 'z': 3}
    >>> callsign.arguments(params, {'x': 'hello'}, safe=True)
    ('hello',), {'y': 2, 'z': 3}
    """
    mutators = mutators or dict()
    if not safe:
        return {p.name: mutators.get(p.name, p.arg) for p in params.values()}

    positionals = *(mutators.get(p.name, p.arg) for p in params.values()
                    if p.kind == ParamKinds.POSITIONAL_ONLY),

    keywords = {p.name: mutators.get(p.name, p.arg) for p in params.values()
                if p.kind != ParamKinds.POSITIONAL_ONLY}

    return positionals, keywords


class CallSign(ModuleType):

    def __init__(self):
        super().__init__(__name__)
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(
        self,
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


sys.modules[__name__] = CallSign()

