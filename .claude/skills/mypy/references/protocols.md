# Protocols and structural subtyping

The Python type system supports two ways of deciding whether two objects are
compatible as types: nominal subtyping and structural subtyping.

*Nominal* subtyping is strictly based on the class hierarchy. If class `Dog`
inherits class `Animal`, it’s a subtype of `Animal`. Instances of `Dog`
can be used when `Animal` instances are expected. This form of subtyping
is what Python’s type system predominantly uses: it’s easy to
understand and produces clear and concise error messages, and matches how the
native [`isinstance`](https://docs.python.org/3/library/functions.html#isinstance "(in Python v3.14)") check works – based on class
hierarchy.

*Structural* subtyping is based on the operations that can be performed with an
object. Class `Dog` is a structural subtype of class `Animal` if the former
has all attributes and methods of the latter, and with compatible types.

Structural subtyping can be seen as a static equivalent of duck typing, which is
well known to Python programmers. See [**PEP 544**](https://peps.python.org/pep-0544/) for the detailed specification
of protocols and structural subtyping in Python.

## Predefined protocols

The [`collections.abc`](https://docs.python.org/3/library/collections.abc.html#module-collections.abc "(in Python v3.14)"), [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") and other stdlib modules define
various protocol classes that correspond to common Python protocols, such as
[`Iterable[T]`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable "(in Python v3.14)"). If a class
defines a suitable [`__iter__`](https://docs.python.org/3/reference/datamodel.html#object.__iter__ "(in Python v3.14)") method, mypy understands that it
implements the iterable protocol and is compatible with [`Iterable[T]`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable "(in Python v3.14)").
For example, `IntList` below is iterable, over `int` values:

```
from __future__ import annotations

from collections.abc import Iterator, Iterable

class IntList:
    def __init__(self, value: int, next: IntList | None) -> None:
        self.value = value
        self.next = next

    def __iter__(self) -> Iterator[int]:
        current = self
        while current:
            yield current.value
            current = current.next

def print_numbered(items: Iterable[int]) -> None:
    for n, x in enumerate(items):
        print(n + 1, x)

x = IntList(3, IntList(5, None))
print_numbered(x)  # OK
print_numbered([4, 5])  # Also OK
```

[Predefined protocol reference](#predefined-protocols-reference) lists various protocols defined in
[`collections.abc`](https://docs.python.org/3/library/collections.abc.html#module-collections.abc "(in Python v3.14)") and [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") and the signatures of the corresponding methods
you need to define to implement each protocol.

Note

`typing` also contains deprecated aliases to protocols and ABCs defined in
[`collections.abc`](https://docs.python.org/3/library/collections.abc.html#module-collections.abc "(in Python v3.14)"), such as [`Iterable[T]`](https://docs.python.org/3/library/typing.html#typing.Iterable "(in Python v3.14)").
These are only necessary in Python 3.8 and earlier, since the protocols in
`collections.abc` didn’t yet support subscripting (`[]`) in Python 3.8,
but the aliases in `typing` have always supported
subscripting. In Python 3.9 and later, the aliases in `typing` don’t provide
any extra functionality.

## Simple user-defined protocols

You can define your own protocol class by inheriting the special `Protocol`
class:

```
from collections.abc import Iterable
from typing import Protocol

class SupportsClose(Protocol):
    # Empty method body (explicit '...')
    def close(self) -> None: ...

class Resource:  # No SupportsClose base class!

    def close(self) -> None:
       self.resource.release()

    # ... other methods ...

def close_all(items: Iterable[SupportsClose]) -> None:
    for item in items:
        item.close()

close_all([Resource(), open('some/file')])  # OK
```

`Resource` is a subtype of the `SupportsClose` protocol since it defines
a compatible `close` method. Regular file objects returned by [`open()`](https://docs.python.org/3/library/functions.html#open "(in Python v3.14)") are
similarly compatible with the protocol, as they support `close()`.

## Defining subprotocols and subclassing protocols

You can also define subprotocols. Existing protocols can be extended
and merged using multiple inheritance. Example:

```
# ... continuing from the previous example

class SupportsRead(Protocol):
    def read(self, amount: int) -> bytes: ...

class TaggedReadableResource(SupportsClose, SupportsRead, Protocol):
    label: str

class AdvancedResource(Resource):
    def __init__(self, label: str) -> None:
        self.label = label

    def read(self, amount: int) -> bytes:
        # some implementation
        ...

resource: TaggedReadableResource
resource = AdvancedResource('handle with care')  # OK
```

Note that inheriting from an existing protocol does not automatically
turn the subclass into a protocol – it just creates a regular
(non-protocol) class or ABC that implements the given protocol (or
protocols). The `Protocol` base class must always be explicitly
present if you are defining a protocol:

```
class NotAProtocol(SupportsClose):  # This is NOT a protocol
    new_attr: int

class Concrete:
   new_attr: int = 0

   def close(self) -> None:
       ...

# Error: nominal subtyping used by default
x: NotAProtocol = Concrete()  # Error!
```

You can also include default implementations of methods in
protocols. If you explicitly subclass these protocols you can inherit
these default implementations.

Explicitly including a protocol as a
base class is also a way of documenting that your class implements a
particular protocol, and it forces mypy to verify that your class
implementation is actually compatible with the protocol. In particular,
omitting a value for an attribute or a method body will make it implicitly
abstract:

```
class SomeProto(Protocol):
    attr: int  # Note, no right hand side
    def method(self) -> str: ...  # Literally just ... here

class ExplicitSubclass(SomeProto):
    pass

ExplicitSubclass()  # error: Cannot instantiate abstract class 'ExplicitSubclass'
                    # with abstract attributes 'attr' and 'method'
```

Similarly, explicitly assigning to a protocol instance can be a way to ask the
type checker to verify that your class implements a protocol:

```
_proto: SomeProto = cast(ExplicitSubclass, None)
```

## Invariance of protocol attributes

A common issue with protocols is that protocol attributes are invariant.
For example:

```
class Box(Protocol):
      content: object

class IntBox:
      content: int

def takes_box(box: Box) -> None: ...

takes_box(IntBox())  # error: Argument 1 to "takes_box" has incompatible type "IntBox"; expected "Box"
                     # note:  Following member(s) of "IntBox" have conflicts:
                     # note:      content: expected "object", got "int"
```

This is because `Box` defines `content` as a mutable attribute.
Here’s why this is problematic:

```
def takes_box_evil(box: Box) -> None:
    box.content = "asdf"  # This is bad, since box.content is supposed to be an object

my_int_box = IntBox()
takes_box_evil(my_int_box)
my_int_box.content + 1  # Oops, TypeError!
```

This can be fixed by declaring `content` to be read-only in the `Box`
protocol using `@property`:

```
class Box(Protocol):
    @property
    def content(self) -> object: ...

class IntBox:
    content: int

def takes_box(box: Box) -> None: ...

takes_box(IntBox(42))  # OK
```

## Recursive protocols

Protocols can be recursive (self-referential) and mutually
recursive. This is useful for declaring abstract recursive collections
such as trees and linked lists:

```
from __future__ import annotations

from typing import Protocol

class TreeLike(Protocol):
    value: int

    @property
    def left(self) -> TreeLike | None: ...

    @property
    def right(self) -> TreeLike | None: ...

class SimpleTree:
    def __init__(self, value: int) -> None:
        self.value = value
        self.left: SimpleTree | None = None
        self.right: SimpleTree | None = None

root: TreeLike = SimpleTree(0)  # OK
```

## Using isinstance() with protocols

You can use a protocol class with [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance "(in Python v3.14)") if you decorate it
with the `@runtime_checkable` class decorator. The decorator adds
rudimentary support for runtime structural checks:

```
from typing import Protocol, runtime_checkable

@runtime_checkable
class Portable(Protocol):
    handles: int

class Mug:
    def __init__(self) -> None:
        self.handles = 1

def use(handles: int) -> None: ...

mug = Mug()
if isinstance(mug, Portable):  # Works at runtime!
   use(mug.handles)
```

[`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance "(in Python v3.14)") also works with the [predefined protocols](#predefined-protocols)
in [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") such as [`Iterable`](https://docs.python.org/3/library/typing.html#typing.Iterable "(in Python v3.14)").

Warning

[`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance "(in Python v3.14)") with protocols is not completely safe at runtime.
For example, signatures of methods are not checked. The runtime
implementation only checks that all protocol members exist,
not that they have the correct type. [`issubclass()`](https://docs.python.org/3/library/functions.html#issubclass "(in Python v3.14)") with protocols
will only check for the existence of methods.

Note

[`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance "(in Python v3.14)") with protocols can also be surprisingly slow.
In many cases, you’re better served by using [`hasattr()`](https://docs.python.org/3/library/functions.html#hasattr "(in Python v3.14)") to
check for the presence of attributes.

## Callback protocols

Protocols can be used to define flexible callback types that are hard
(or even impossible) to express using the
[`Callable[...]`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable "(in Python v3.14)") syntax,
such as variadic, overloaded, and complex generic callbacks. They are defined with a
special [`__call__`](https://docs.python.org/3/reference/datamodel.html#object.__call__ "(in Python v3.14)") member:

```
from collections.abc import Iterable
from typing import Optional, Protocol

class Combiner(Protocol):
    def __call__(self, *vals: bytes, maxlen: int | None = None) -> list[bytes]: ...

def batch_proc(data: Iterable[bytes], cb_results: Combiner) -> bytes:
    for item in data:
        ...

def good_cb(*vals: bytes, maxlen: int | None = None) -> list[bytes]:
    ...
def bad_cb(*vals: bytes, maxitems: int | None) -> list[bytes]:
    ...

batch_proc([], good_cb)  # OK
batch_proc([], bad_cb)   # Error! Argument 2 has incompatible type because of
                         # different name and kind in the callback
```

Callback protocols and [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable "(in Python v3.14)") types can be used mostly interchangeably.
Parameter names in [`__call__`](https://docs.python.org/3/reference/datamodel.html#object.__call__ "(in Python v3.14)") methods must be identical, unless
the parameters are positional-only. Example (using the legacy syntax for generic functions):

```
from collections.abc import Callable
from typing import Protocol, TypeVar

T = TypeVar('T')

class Copy(Protocol):
    # '/' marks the end of positional-only parameters
    def __call__(self, origin: T, /) -> T: ...

copy_a: Callable[[T], T]
copy_b: Copy

copy_a = copy_b  # OK
copy_b = copy_a  # Also OK
```

## Binding of types in protocol attributes

All protocol attributes annotations are treated as externally visible types
of those attributes. This means that for example callables are not bound,
and descriptors are not invoked:

```
from typing import Callable, Protocol, overload

class Integer:
    @overload
    def __get__(self, instance: None, owner: object) -> Integer: ...
    @overload
    def __get__(self, instance: object, owner: object) -> int: ...
    # <some implementation>

class Example(Protocol):
    foo: Callable[[object], int]
    bar: Integer

ex: Example
reveal_type(ex.foo)  # Revealed type is Callable[[object], int]
reveal_type(ex.bar)  # Revealed type is Integer
```

In other words, protocol attribute types are handled as they would appear in a
`self` attribute annotation in a regular class. If you want some protocol
attributes to be handled as though they were defined at class level, you should
declare them explicitly using `ClassVar[...]`. Continuing previous example:

```
from typing import ClassVar

class OtherExample(Protocol):
    # This style is *not recommended*, but may be needed to reuse
    # some complex callable types. Otherwise use regular methods.
    foo: ClassVar[Callable[[object], int]]
    # This may be needed to mimic descriptor access on Type[...] types,
    # otherwise use a plain "bar: int" style.
    bar: ClassVar[Integer]

ex2: OtherExample
reveal_type(ex2.foo)  # Revealed type is Callable[[], int]
reveal_type(ex2.bar)  # Revealed type is int
```

## Predefined protocol reference

### Iteration protocols

The iteration protocols are useful in many contexts. For example, they allow
iteration of objects in for loops.

#### collections.abc.Iterable[T]

The [example above](#predefined-protocols) has a simple implementation of an
[`__iter__`](https://docs.python.org/3/reference/datamodel.html#object.__iter__ "(in Python v3.14)") method.

```
def __iter__(self) -> Iterator[T]
```

See also [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable "(in Python v3.14)").

#### collections.abc.Iterator[T]

```
def __next__(self) -> T
def __iter__(self) -> Iterator[T]
```

See also [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator "(in Python v3.14)").

### Collection protocols

Many of these are implemented by built-in container types such as
[`list`](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.14)") and [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)"), and these are also useful for user-defined
collection objects.

#### collections.abc.Sized

This is a type for objects that support [`len(x)`](https://docs.python.org/3/library/functions.html#len "(in Python v3.14)").

```
def __len__(self) -> int
```

See also [`Sized`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sized "(in Python v3.14)").

#### collections.abc.Container[T]

This is a type for objects that support the `in` operator.

```
def __contains__(self, x: object) -> bool
```

See also [`Container`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Container "(in Python v3.14)").

#### collections.abc.Collection[T]

```
def __len__(self) -> int
def __iter__(self) -> Iterator[T]
def __contains__(self, x: object) -> bool
```

See also [`Collection`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Collection "(in Python v3.14)").

### One-off protocols

These protocols are typically only useful with a single standard
library function or class.

#### collections.abc.Reversible[T]

This is a type for objects that support [`reversed(x)`](https://docs.python.org/3/library/functions.html#reversed "(in Python v3.14)").

```
def __reversed__(self) -> Iterator[T]
```

See also [`Reversible`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Reversible "(in Python v3.14)").

#### typing.SupportsAbs[T]

This is a type for objects that support [`abs(x)`](https://docs.python.org/3/library/functions.html#abs "(in Python v3.14)"). `T` is the type of
value returned by [`abs(x)`](https://docs.python.org/3/library/functions.html#abs "(in Python v3.14)").

```
def __abs__(self) -> T
```

See also [`SupportsAbs`](https://docs.python.org/3/library/typing.html#typing.SupportsAbs "(in Python v3.14)").

#### typing.SupportsBytes

This is a type for objects that support [`bytes(x)`](https://docs.python.org/3/library/stdtypes.html#bytes "(in Python v3.14)").

```
def __bytes__(self) -> bytes
```

See also [`SupportsBytes`](https://docs.python.org/3/library/typing.html#typing.SupportsBytes "(in Python v3.14)").

#### typing.SupportsComplex

This is a type for objects that support [`complex(x)`](https://docs.python.org/3/library/functions.html#complex "(in Python v3.14)"). Note that no arithmetic operations
are supported.

```
def __complex__(self) -> complex
```

See also [`SupportsComplex`](https://docs.python.org/3/library/typing.html#typing.SupportsComplex "(in Python v3.14)").

#### typing.SupportsFloat

This is a type for objects that support [`float(x)`](https://docs.python.org/3/library/functions.html#float "(in Python v3.14)"). Note that no arithmetic operations
are supported.

```
def __float__(self) -> float
```

See also [`SupportsFloat`](https://docs.python.org/3/library/typing.html#typing.SupportsFloat "(in Python v3.14)").

#### typing.SupportsInt

This is a type for objects that support [`int(x)`](https://docs.python.org/3/library/functions.html#int "(in Python v3.14)"). Note that no arithmetic operations
are supported.

```
def __int__(self) -> int
```

See also [`SupportsInt`](https://docs.python.org/3/library/typing.html#typing.SupportsInt "(in Python v3.14)").

#### typing.SupportsRound[T]

This is a type for objects that support [`round(x)`](https://docs.python.org/3/library/functions.html#round "(in Python v3.14)").

```
def __round__(self) -> T
```

See also [`SupportsRound`](https://docs.python.org/3/library/typing.html#typing.SupportsRound "(in Python v3.14)").

### Async protocols

These protocols can be useful in async code. See [Typing async/await](more_types.html#async-and-await)
for more information.

#### collections.abc.Awaitable[T]

```
def __await__(self) -> Generator[Any, None, T]
```

See also [`Awaitable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Awaitable "(in Python v3.14)").

#### collections.abc.AsyncIterable[T]

```
def __aiter__(self) -> AsyncIterator[T]
```

See also [`AsyncIterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterable "(in Python v3.14)").

#### collections.abc.AsyncIterator[T]

```
def __anext__(self) -> Awaitable[T]
def __aiter__(self) -> AsyncIterator[T]
```

See also [`AsyncIterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator "(in Python v3.14)").

### Context manager protocols

There are two protocols for context managers – one for regular context
managers and one for async ones. These allow defining objects that can
be used in `with` and `async with` statements.

#### contextlib.AbstractContextManager[T]

```
def __enter__(self) -> T
def __exit__(self,
             exc_type: type[BaseException] | None,
             exc_value: BaseException | None,
             traceback: TracebackType | None) -> bool | None
```

See also [`AbstractContextManager`](https://docs.python.org/3/library/contextlib.html#contextlib.AbstractContextManager "(in Python v3.14)").

#### contextlib.AbstractAsyncContextManager[T]

```
def __aenter__(self) -> Awaitable[T]
def __aexit__(self,
              exc_type: type[BaseException] | None,
              exc_value: BaseException | None,
              traceback: TracebackType | None) -> Awaitable[bool | None]
```

See also [`AbstractAsyncContextManager`](https://docs.python.org/3/library/contextlib.html#contextlib.AbstractAsyncContextManager "(in Python v3.14)").