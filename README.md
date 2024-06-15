<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap" rel="stylesheet">

<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap');

.orbitron-title {
  font-family: "Orbitron", sans-serif;
  font-optical-sizing: auto;
  font-weight: 400;
  font-style: normal;
}

.side-by-side {
  display: flex;
}

.image-stuff {
  border-radius: 25px;
  width: 125px;
  height: 125px;
  margin-right: 15px;
}

</style>

<div class="side-by-side">
  <img src="imgs/mainlogo.png" class="image-stuff"/>
  <h1 class="orbitron-title">callsign: simplified introspection</h1>
</div>
<br>


callsign; a python package that abstracts away boilerplate from the  standard
library's inspect module. Made for practitioners of DDD 
(decorator driven development); minimizing tedium and keeping things
DRY is what we're all about.

Only dependency is python 3 .


## Installation

`pip install callsign`

## Usage

```python
>>> import callsign

>>> def f(x, y: int): return x, y

>>> params = callsign(f, 'hi', y=2)
>>> params  # a dict of namedtuples
{
    'x': Paramattrs(name='x',
                    arg='hi',
                    default=inspect._empty,
                    kind=ParamKinds.POSITIONAL_OR_KEYWORD,
                    defaulted=False,
                    annotation=inspect._empty),
    'y': Paramattrs(name='y',
                    arg=2,
                    default=inspect._empty,
                    kind=ParamKinds.POSITIONAL_OR_KEYWORD,
                    defaulted=False,
                    annotation=<class 'int'>),
}

>>> params['x'].arg
'hi'

>>> params['x'].annotation
inspect._empty
>>> callsign.isempty(params['x'].annotation)
True

>>> params['y'].annotation
<class 'int'>
```

Any time you do a callsign of a function and its positional + keyword arguments,
you'll get a python dictionary back of each parameter name
mapped to its _Paramattrs_ (the param's attributes).

### Recipes

#### Basic DDD

```python
import callsign

def decorator(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def newfn(*args, **kwargs) -> Any:

        # introspection!
        params = callsign(fn, *args, **kwargs)

        if params['x'].defaulted:
            return fn(*args, **kwargs)
        elif params['y'].arg == 'something else':
            return fn('doing something with y')

        ...
    return newfn  # and bob's your uncle
```

#### Build a rudimentary type checker

```python
import callsign

def type_checker(fn: Callable[..., [Any]]) -> Callable[..., [Any | NoReturn]]:
    @functools.wraps(fn)
    def typedfn(*args, **kwargs) -> Any:
    
        params = callsign(fn, *args, **kwargs)

        for param in params:
            if param.annotation and type(param.arg) != param.annotation:
                raise TypeError()

        return fn(*args, **kwargs)  # and bob's your uncle!
    return typedfn
```

#### Advanced DDD

```python
import callsign

def decorator(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def newfn(*args, **kwargs) -> Any:
        params = callsign(fn, *args, **kwargs)
       
        mut = {'x': 2, 'y': 3}
        positionals, keywords = callsign.arguments(params, mut, safe=True)
        return fn(*positionals, **keywords)
    return newfn

@decorator
def crazy_signature(x, /, *args, y=10, **kwargs): return x, args, y, kwargs

x, _, y, _ = crazy_signature(10, y=20)
print(x)  # 2
print(y)  # 3
```
### Paramattrs

The _Paramattrs_ object is a pure python namedtuple, nothing fancy. It defines
the following attributes:

* name: the parameter's name
* arg: the given argument
* default: if a default value was assigned to the function's signature, it's
preserved here, otherwise it's `inspect.empty`
* kind: one of a _ParamKinds_ Enum
* defaulted: this is `True` if no argument is given and a default is being used
* annotation: this will be `inspect._empty` if no type hint is written
in the function signature, otherwise it will be whatever was provided as
a type hint

### ParamKinds

These are taken from the standard library's inspect module, but we've added one:
`ParamKinds.VULNERABLE_DEFAULT`. 

VULNERABLE\_DEFAULT is interchangeable with POSITIONAL\_OR\_KEYWORD; but also,
it is a parameter that was given a default value, and that default
has been overridden by a VARARGS parameter, e.g.:

```python
>>> def hello(x=10, *args): return x, args

>>> print( hello() )
(10, ())

>>> print( hello(1, 2, 3) )
(1, (2, 3))  # x = 10 was overridden, x is now 1
```

