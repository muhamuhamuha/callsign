"""
>>> import callsign
>>> f = lambda x, y: (x, y)
>>> params = callsign(f, 'hi', y=2)
>>> params
{
    'x': Paramattr(name='x',
                   value='hi',
                   default=inspect._empty,
                   kind=ParamKinds.POSITIONAL_OR_KEYWORD,
                   annotation=inspect._empty
                  ),

    'y': Paramattr(name='y',
                   value=2,
                   default=inspect._empty,
                   kind=ParamKinds.POSITIONAL_OR_KEYWORD,
                   annotation=inspect._empty
                  ),
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

from types import ModuleType
from typing import (
    Any,
    Callable,
    NamedTuple,
)

from constants import ParamKinds


class Paramattr(NamedTuple):
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
    | annotation | Any or         | If the function's parameters have type    |
    |            | inspect._empty | hints they are included here; otherwise   |
    |            |                | it's inspect._empty                       |
    +------------+----------------+-------------------------------------------+
    """
    name: str
    value: Any
    default: Any | inspect._empty
    kind: ParamKinds
    defaulted: bool
    annotation: Any | inspect._empty


def _create_paramattrs(bargs: inspect.BoundArguments,
                       params: dict[str, inspect.Parameter]
                       ) -> dict[str, Paramattr]:

    # gather all the kinds of parameters that were passed to the function
    kinds = (params[pname].kind.name for pname in params)

    paramattrs = dict()
    for pname in params:
        pobj = params[pname]

        value = bargs.arguments.get(pname, pobj.default)
        default = pobj.default
        kind = ParamKinds(pobj.kind.name)
        defaulted = bargs.arguments.get(pname, inspect._empty) is inspect._empty
        annotation = pobj.annotation or inspect._empty

        # find any VULNERABLE_DEFAULT(s)
        if (ParamKinds.VAR_POSITIONAL in kinds
            and kind == ParamKinds.POSITIONAL_OR_KEYWORD
            and value != default
            and default is not inspect._empty):

            kind = ParamKinds.VULNERABLE_DEFAULT

        paramattrs[pname] = Paramattr(pname, value, default, kind, defaulted,
                                      annotation)

    return paramattrs


class CallSign(ModuleType):

    def __init__(self):
        super().__init__(__name__)
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __call__(self,
                 fn: Callable,
                 *args: Any,
                 **kwargs: Any,
                 ) -> dict[str, Paramattr]:

        sig = inspect.signature(fn)
        bargs = sig.bind_partial(*args, **kwargs)
        # don't use bargs.apply_defaults, we will apply manually

        paramattrs = _create_paramattrs(bargs, sig.parameters)
        return paramattrs

    @staticmethod
    def isempty(whatever: Any) -> bool:
        """
        >>> import inspect, callsign
        >>> callsign.isempty(inspect._empty)
        True
        """
        return whatever is inspect._empty


sys.modules[__name__] = CallSign()

