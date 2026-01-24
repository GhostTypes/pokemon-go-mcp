# Metaclasses

A [metaclass](https://docs.python.org/3/reference/datamodel.html#metaclasses "(in Python v3.14)") is a class that describes
the construction and behavior of other classes, similarly to how classes
describe the construction and behavior of objects.
The default metaclass is [`type`](https://docs.python.org/3/library/functions.html#type "(in Python v3.14)"), but it’s possible to use other metaclasses.
Metaclasses allows one to create “a different kind of class”, such as
[`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum "(in Python v3.14)")s, [`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple "(in Python v3.14)")s and singletons.

Mypy has some special understanding of [`ABCMeta`](https://docs.python.org/3/library/abc.html#abc.ABCMeta "(in Python v3.14)") and `EnumMeta`.

## Defining a metaclass

```
class M(type):
    pass

class A(metaclass=M):
    pass
```

## Metaclass usage example

Mypy supports the lookup of attributes in the metaclass:

```
from typing import ClassVar, TypeVar

S = TypeVar("S")

class M(type):
    count: ClassVar[int] = 0

    def make(cls: type[S]) -> S:
        M.count += 1
        return cls()

class A(metaclass=M):
    pass

a: A = A.make()  # make() is looked up at M; the result is an object of type A
print(A.count)

class B(A):
    pass

b: B = B.make()  # metaclasses are inherited
print(B.count + " objects were created")  # Error: Unsupported operand types for + ("int" and "str")
```

## Gotchas and limitations of metaclass support

Note that metaclasses pose some requirements on the inheritance structure,
so it’s better not to combine metaclasses and class hierarchies:

```
class M1(type): pass
class M2(type): pass

class A1(metaclass=M1): pass
class A2(metaclass=M2): pass

class B1(A1, metaclass=M2): pass  # Mypy Error: metaclass conflict
# At runtime the above definition raises an exception
# TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

class B12(A1, A2): pass  # Mypy Error: metaclass conflict

# This can be solved via a common metaclass subtype:
class CorrectMeta(M1, M2): pass
class B2(A1, A2, metaclass=CorrectMeta): pass  # OK, runtime is also OK
```

* Mypy does not understand dynamically-computed metaclasses,
  such as `class A(metaclass=f()): ...`
* Mypy does not and cannot understand arbitrary metaclass code.
* Mypy only recognizes subclasses of [`type`](https://docs.python.org/3/library/functions.html#type "(in Python v3.14)") as potential metaclasses.
* `Self` is not allowed as annotation in metaclasses as per [PEP 673](https://peps.python.org/pep-0673/#valid-locations-for-self).

For some builtin types, mypy may think their metaclass is [`abc.ABCMeta`](https://docs.python.org/3/library/abc.html#abc.ABCMeta "(in Python v3.14)")
even if it is [`type`](https://docs.python.org/3/library/functions.html#type "(in Python v3.14)") at runtime. In those cases, you can either:

* use [`abc.ABCMeta`](https://docs.python.org/3/library/abc.html#abc.ABCMeta "(in Python v3.14)") instead of [`type`](https://docs.python.org/3/library/functions.html#type "(in Python v3.14)") as the
  superclass of your metaclass if that works in your use-case
* mute the error with `# type: ignore[metaclass]`

```
import abc

assert type(tuple) is type  # metaclass of tuple is type at runtime

# The problem:
class M0(type): pass
class A0(tuple, metaclass=M0): pass  # Mypy Error: metaclass conflict

# Option 1: use ABCMeta instead of type
class M1(abc.ABCMeta): pass
class A1(tuple, metaclass=M1): pass

# Option 2: mute the error
class M2(type): pass
class A2(tuple, metaclass=M2): pass  # type: ignore[metaclass]
```