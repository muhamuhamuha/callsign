import pytest
import functools
from typing import Callable, Any, NoReturn
import callsign

## RUDIMENTARY TYPE CHECKER

def type_checker(fn: Callable[..., [Any]]) -> Callable[..., [Any | NoReturn]]:
    @functools.wraps(fn)
    def typedfn(*args, **kwargs) -> Any:
        params = callsign(fn, *args, **kwargs)

        for param in params.values():
            if not callsign.isempty(param.annotation) and type(param.arg) != param.annotation:
                raise TypeError(f"Parameter '{param.name}' is expected to be "
                                f"of type {param.annotation.__name__}, but got "
                                f"{type(param.arg).__name__}")

        return fn(*args, **kwargs)
    return typedfn

# Test functions
@type_checker
def add(x: int, y: int) -> int: return x + y

@type_checker
def greet(name: str, greeting: str = "Hello") -> str: return f"{greeting}, {name}"

@type_checker
def multiply(x: float, y: float) -> float: return x * y

@type_checker
def concat_strings(a: str, b: str) -> str: return a + b


def test_add_correct_types():
    assert add(1, 2) == 3


def test_add_incorrect_types():
    with pytest.raises(TypeError):
        add(1, "2")


def test_greet_correct_types():
    assert greet("Alice") == "Hello, Alice"


def test_greet_incorrect_types():
    with pytest.raises(TypeError):
        greet(123)


def test_greet_correct_types_with_kwargs():
    assert greet("Alice", greeting="Hi") == "Hi, Alice"


def test_multiply_correct_types():
    assert multiply(2.0, 3.0) == 6.0


def test_multiply_incorrect_types():
    with pytest.raises(TypeError):
        multiply(2.0, "3.0")


def test_concat_strings_correct_types():
    assert concat_strings("Hello", " World") == "Hello World"


def test_concat_strings_incorrect_types():
    with pytest.raises(TypeError):
        concat_strings("Hello", 123)


