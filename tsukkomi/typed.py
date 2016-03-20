""":mod:`tsukkomi.typed` --- A functions check types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import functools
import inspect
import typing

__all__ = ('check_arguments', 'check_callable', 'check_return', 'check_type',
           'typechecked', )


T = typing.TypeVar('T')


def check_type(value: typing.Any, hint: type) -> bool:
    """Check given ``value``'s type.

    :param value: given argument
    :param hint: assumed type of given ``value``

    """
    if type(hint) is typing.CallableMeta:
        actual_type, correct = check_callable(value, hint)
    else:
        correct = isinstance(value, hint)
        actual_type = type(value)
    return actual_type, correct


def check_return(callable_name: str, r: typing.Any,
                 hints: typing.Mapping[str, type]) -> None:
    """Check return type, raise :class:`TypeError` if return type is not
    expected type.

    :param str callable_name: callable name of :func:`~.typechecked` checked
    :param r: returned result
    :param hints: assumed type of given ``r``

    """
    correct = True
    _, checks = check_type(r, hints['return'])
    if not correct:
        raise TypeError(
            'Incorrect return type `{}`, expected {}. for: {}'.format(
                type(r), hints.get('return'), callable_name
            )
        )


def check_callable(callable_: typing.Callable, hint: type) -> bool:
    """Check argument type & return type of :class:`typing.Callable`. since it
    raises check :class:`typing.Callable` using `isinstance`, so compare in
    diffrent way

    :param callable_: callable object given as a argument
    :param hint: assumed type of given ``callable_``

    """
    hints = typing.get_type_hints(callable_)
    return_type = hints.pop('return', type(None))
    signature = inspect.signature(callable_)
    arg_types = (param.annotation for _, param in signature.parameters.items())
    correct = hint.__args__ == arg_types and hint.__result__ == return_type
    return typing.Callable[list(arg_types), return_type], correct


def check_arguments(c: typing.Callable, hints: typing.Mapping[str, type],
                    *args, **kwargs) -> None:
    """Check arguments type, raise :class:`TypeError` if argument type is not
    expected type.

    :param c: callable object want to check types
    :param hints: assumed type of given ``c`` result of
                  :func:`typing.get_type_hints`

    """
    signature = inspect.signature(c)
    bound = signature.bind(*args, **kwargs)
    for argument_name, value in bound.arguments.items():
        type_hint = hints.get(argument_name)
        if type_hint is None:
            continue
        actual_type, correct = check_type(value, type_hint)
        if not correct:
            raise TypeError(
                'Incorrect type `{}`, expected `{}` for `{}`'.format(
                    actual_type, type_hint, argument_name
                )
            )


def typechecked(c: typing.Callable[..., T]) -> T:
    """A decorator to make a callable object checks its types

    .. code-block:: python

       from typing import Callable

       @typechecked
       def foobar(x: str) -> bool:
           return x == 'hello world'


       @typechecked
       def hello_world(foo: str, bar: Callable[[str], bool]) -> bool:
           return bar(foo)


       hello_world('hello world', foobar)
       hello_world(3.14, foobar) # it raise TypeError


    :param c: callable object want to check types
    :type c: :class:`typing.Callable`
    :return:

    """
    @functools.wraps(c)
    def decorator(*args, **kwargs):
        hints = typing.get_type_hints(c)
        check_arguments(c, hints, *args, **kwargs)
        result = c(*args, **kwargs)
        check_return(c.__name__, result, hints)
        return result

    return decorator