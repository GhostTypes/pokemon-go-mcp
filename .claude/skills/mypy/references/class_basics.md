# Class basics

This section will help get you started annotating your
classes. Built-in classes such as `int` also follow these same
rules.

## Instance and class attributes

The mypy type checker detects if you are trying to access a missing
attribute, which is a very common programming error. For this to work
correctly, instance and class attributes must be defined or
initialized within the class. Mypy infers the types of attributes:

```
class A:
    def __init__(self, x: int) -> None:
        self.x = x  # Aha, attribute 'x' of type 'int'

a = A(1)
a.x = 2  # OK!
a.y = 3  # Error: "A" has no attribute "y"
```

This is a bit like each class having an implicitly defined
[`__slots__`](https://docs.python.org/3/reference/datamodel.html#object.__slots__ "(in Python v3.14)") attribute. This is only enforced during type
checking and not when your program is running.

You can declare types of variables in the class body explicitly using
a type annotation:

```
class A:
    x: list[int]  # Declare attribute 'x' of type list[int]

a = A()
a.x = [1]     # OK
```

As in Python generally, a variable defined in the class body can be used
as a class or an instance variable. (As discussed in the next section, you
can override this with a [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") annotation.)

Similarly, you can give explicit types to instance variables defined
in a method:

```
class A:
    def __init__(self) -> None:
        self.x: list[int] = []

    def f(self) -> None:
        self.y: Any = 0
```

You can only define an instance variable within a method if you assign
to it explicitly using `self`:

```
class A:
    def __init__(self) -> None:
        self.y = 1   # Define 'y'
        a = self
        a.x = 1      # Error: 'x' not defined
```

## Annotating \_\_init\_\_ methods

The [`__init__`](https://docs.python.org/3/reference/datamodel.html#object.__init__ "(in Python v3.14)") method is somewhat special – it doesn’t return a
value. This is best expressed as `-> None`. However, since many feel
this is redundant, it is allowed to omit the return type declaration
on [`__init__`](https://docs.python.org/3/reference/datamodel.html#object.__init__ "(in Python v3.14)") methods **if at least one argument is annotated**. For
example, in the following classes [`__init__`](https://docs.python.org/3/reference/datamodel.html#object.__init__ "(in Python v3.14)") is considered fully
annotated:

```
class C1:
    def __init__(self) -> None:
        self.var = 42

class C2:
    def __init__(self, arg: int):
        self.var = arg
```

However, if [`__init__`](https://docs.python.org/3/reference/datamodel.html#object.__init__ "(in Python v3.14)") has no annotated arguments and no return type
annotation, it is considered an untyped method:

```
class C3:
    def __init__(self):
        # This body is not type checked
        self.var = 42 + 'abc'
```

## Class attribute annotations

You can use a [`ClassVar[t]`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") annotation to explicitly declare that a
particular attribute should not be set on instances:

```
from typing import ClassVar

class A:
    x: ClassVar[int] = 0  # Class variable only

A.x += 1  # OK

a = A()
a.x = 1  # Error: Cannot assign to class variable "x" via instance
print(a.x)  # OK -- can be read through an instance
```

It’s not necessary to annotate all class variables using
[`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)"). An attribute without the [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") annotation can
still be used as a class variable. However, mypy won’t prevent it from
being used as an instance variable, as discussed previously:

```
class A:
    x = 0  # Can be used as a class or instance variable

A.x += 1  # OK

a = A()
a.x = 1  # Also OK
```

Note that [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") is not a class, and you can’t use it with
[`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance "(in Python v3.14)") or [`issubclass()`](https://docs.python.org/3/library/functions.html#issubclass "(in Python v3.14)"). It does not change Python
runtime behavior – it’s only for type checkers such as mypy (and
also helpful for human readers).

You can also omit the square brackets and the variable type in
a [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") annotation, but this might not do what you’d expect:

```
class A:
    y: ClassVar = 0  # Type implicitly Any!
```

In this case the type of the attribute will be implicitly `Any`.
This behavior will change in the future, since it’s surprising.

An explicit [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") may be particularly handy to distinguish
between class and instance variables with callable types. For example:

```
from collections.abc import Callable
from typing import ClassVar

class A:
    foo: Callable[[int], None]
    bar: ClassVar[Callable[[A, int], None]]
    bad: Callable[[A], None]

A().foo(42)  # OK
A().bar(42)  # OK
A().bad()  # Error: Too few arguments
```

Note

A [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar "(in Python v3.14)") type parameter cannot include type variables:
`ClassVar[T]` and `ClassVar[list[T]]`
are both invalid if `T` is a type variable (see [Defining generic classes](generics.html#generic-classes)
for more about type variables).

## Overriding statically typed methods

When overriding a statically typed method, mypy checks that the
override has a compatible signature:

```
class Base:
    def f(self, x: int) -> None:
        ...

class Derived1(Base):
    def f(self, x: str) -> None:   # Error: type of 'x' incompatible
        ...

class Derived2(Base):
    def f(self, x: int, y: int) -> None:  # Error: too many arguments
        ...

class Derived3(Base):
    def f(self, x: int) -> None:   # OK
        ...

class Derived4(Base):
    def f(self, x: float) -> None:   # OK: mypy treats int as a subtype of float
        ...

class Derived5(Base):
    def f(self, x: int, y: int = 0) -> None:   # OK: accepts more than the base
        ...                                    #     class method
```

Note

You can also vary return types **covariantly** in overriding. For
example, you could override the return type `Iterable[int]` with a
subtype such as `list[int]`. Similarly, you can vary argument types
**contravariantly** – subclasses can have more general argument types.

In order to ensure that your code remains correct when renaming methods,
it can be helpful to explicitly mark a method as overriding a base
method. This can be done with the `@override` decorator. `@override`
can be imported from `typing` starting with Python 3.12 or from
`typing_extensions` for use with older Python versions. If the base
method is then renamed while the overriding method is not, mypy will
show an error:

```
from typing import override

class Base:
    def f(self, x: int) -> None:
        ...
    def g_renamed(self, y: str) -> None:
        ...

class Derived1(Base):
    @override
    def f(self, x: int) -> None:   # OK
        ...

    @override
    def g(self, y: str) -> None:   # Error: no corresponding base method found
        ...
```

Note

Use [–enable-error-code explicit-override](error_code_list2.html#code-explicit-override) to require
that method overrides use the `@override` decorator. Emit an error if it is missing.

You can also override a statically typed method with a dynamically
typed one. This allows dynamically typed code to override methods
defined in library classes without worrying about their type
signatures.

As always, relying on dynamically typed code can be unsafe. There is no
runtime enforcement that the method override returns a value that is
compatible with the original return type, since annotations have no
effect at runtime:

```
class Base:
    def inc(self, x: int) -> int:
        return x + 1

class Derived(Base):
    def inc(self, x):   # Override, dynamically typed
        return 'hello'  # Incompatible with 'Base', but no mypy error
```

## Abstract base classes and multiple inheritance

Mypy supports Python [abstract base classes](https://docs.python.org/3/library/abc.html "(in Python v3.14)") (ABCs). Abstract classes
have at least one abstract method or property that must be implemented
by any *concrete* (non-abstract) subclass. You can define abstract base
classes using the [`abc.ABCMeta`](https://docs.python.org/3/library/abc.html#abc.ABCMeta "(in Python v3.14)") metaclass and the [`@abc.abstractmethod`](https://docs.python.org/3/library/abc.html#abc.abstractmethod "(in Python v3.14)")
function decorator. Example:

```
from abc import ABCMeta, abstractmethod

class Animal(metaclass=ABCMeta):
    @abstractmethod
    def eat(self, food: str) -> None: pass

    @property
    @abstractmethod
    def can_walk(self) -> bool: pass

class Cat(Animal):
    def eat(self, food: str) -> None:
        ...  # Body omitted

    @property
    def can_walk(self) -> bool:
        return True

x = Animal()  # Error: 'Animal' is abstract due to 'eat' and 'can_walk'
y = Cat()     # OK
```

Note that mypy performs checking for unimplemented abstract methods
even if you omit the [`ABCMeta`](https://docs.python.org/3/library/abc.html#abc.ABCMeta "(in Python v3.14)") metaclass. This can be useful if the
metaclass would cause runtime metaclass conflicts.

Since you can’t create instances of ABCs, they are most commonly used in
type annotations. For example, this method accepts arbitrary iterables
containing arbitrary animals (instances of concrete `Animal`
subclasses):

```
def feed_all(animals: Iterable[Animal], food: str) -> None:
    for animal in animals:
        animal.eat(food)
```

There is one important peculiarity about how ABCs work in Python –
whether a particular class is abstract or not is somewhat implicit.
In the example below, `Derived` is treated as an abstract base class
since `Derived` inherits an abstract `f` method from `Base` and
doesn’t explicitly implement it. The definition of `Derived`
generates no errors from mypy, since it’s a valid ABC:

```
from abc import ABCMeta, abstractmethod

class Base(metaclass=ABCMeta):
    @abstractmethod
    def f(self, x: int) -> None: pass

class Derived(Base):  # No error -- Derived is implicitly abstract
    def g(self) -> None:
        ...
```

Attempting to create an instance of `Derived` will be rejected,
however:

```
d = Derived()  # Error: 'Derived' is abstract
```

Note

It’s a common error to forget to implement an abstract method.
As shown above, the class definition will not generate an error
in this case, but any attempt to construct an instance will be
flagged as an error.

Mypy allows you to omit the body for an abstract method, but if you do so,
it is unsafe to call such method via `super()`. For example:

```
from abc import abstractmethod
class Base:
    @abstractmethod
    def foo(self) -> int: pass
    @abstractmethod
    def bar(self) -> int:
        return 0
class Sub(Base):
    def foo(self) -> int:
        return super().foo() + 1  # error: Call to abstract method "foo" of "Base"
                                  # with trivial body via super() is unsafe
    @abstractmethod
    def bar(self) -> int:
        return super().bar() + 1  # This is OK however.
```

A class can inherit any number of classes, both abstract and
concrete. As with normal overrides, a dynamically typed method can
override or implement a statically typed method defined in any base
class, including an abstract method defined in an abstract base class.

You can implement an abstract property using either a normal
property or an instance variable.

## Slots

When a class has explicitly defined [\_\_slots\_\_](https://docs.python.org/3/glossary.html#term-__slots__ "(in Python v3.14)"),
mypy will check that all attributes assigned to are members of `__slots__`:

```
class Album:
    __slots__ = ('name', 'year')

    def __init__(self, name: str, year: int) -> None:
       self.name = name
       self.year = year
       # Error: Trying to assign name "released" that is not in "__slots__" of type "Album"
       self.released = True

my_album = Album('Songs about Python', 2021)
```

Mypy will only check attribute assignments against `__slots__` when
the following conditions hold:

1. All base classes (except builtin ones) must have explicit
   `__slots__` defined (this mirrors Python semantics).
2. `__slots__` does not include `__dict__`. If `__slots__`
   includes `__dict__`, arbitrary attributes can be set, similar to
   when `__slots__` is not defined (this mirrors Python semantics).
3. All values in `__slots__` must be string literals.