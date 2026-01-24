# TypedDict

Python programs often use dictionaries with string keys to represent objects.
`TypedDict` lets you give precise types for dictionaries that represent
objects with a fixed schema, such as `{'id': 1, 'items': ['x']}`.

Here is a typical example:

```
movie = {'name': 'Blade Runner', 'year': 1982}
```

Only a fixed set of string keys is expected (`'name'` and
`'year'` above), and each key has an independent value type (`str`
for `'name'` and `int` for `'year'` above). We’ve previously
seen the `dict[K, V]` type, which lets you declare uniform
dictionary types, where every value has the same type, and arbitrary keys
are supported. This is clearly not a good fit for
`movie` above. Instead, you can use a `TypedDict` to give a precise
type for objects like `movie`, where the type of each
dictionary value depends on the key:

```
from typing import TypedDict

Movie = TypedDict('Movie', {'name': str, 'year': int})

movie: Movie = {'name': 'Blade Runner', 'year': 1982}
```

`Movie` is a `TypedDict` type with two items: `'name'` (with type `str`)
and `'year'` (with type `int`). Note that we used an explicit type
annotation for the `movie` variable. This type annotation is
important – without it, mypy will try to infer a regular, uniform
[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)") type for `movie`, which is not what we want here.

Note

If you pass a `TypedDict` object as an argument to a function, no
type annotation is usually necessary since mypy can infer the
desired type based on the declared argument type. Also, if an
assignment target has been previously defined, and it has a
`TypedDict` type, mypy will treat the assigned value as a `TypedDict`,
not [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)").

Now mypy will recognize these as valid:

```
name = movie['name']  # Okay; type of name is str
year = movie['year']  # Okay; type of year is int
```

Mypy will detect an invalid key as an error:

```
director = movie['director']  # Error: 'director' is not a valid key
```

Mypy will also reject a runtime-computed expression as a key, as
it can’t verify that it’s a valid key. You can only use string
literals as `TypedDict` keys.

The `TypedDict` type object can also act as a constructor. It
returns a normal [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)") object at runtime – a `TypedDict` does
not define a new runtime type:

```
toy_story = Movie(name='Toy Story', year=1995)
```

This is equivalent to just constructing a dictionary directly using
`{ ... }` or `dict(key=value, ...)`. The constructor form is
sometimes convenient, since it can be used without a type annotation,
and it also makes the type of the object explicit.

Like all types, `TypedDict`s can be used as components to build
arbitrarily complex types. For example, you can define nested
`TypedDict`s and containers with `TypedDict` items.
Unlike most other types, mypy uses structural compatibility checking
(or structural subtyping) with `TypedDict`s. A `TypedDict` object with
extra items is compatible with (a subtype of) a narrower
`TypedDict`, assuming item types are compatible (*totality* also affects
subtyping, as discussed below).

A `TypedDict` object is not a subtype of the regular `dict[...]`
type (and vice versa), since [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)") allows arbitrary keys to be
added and removed, unlike `TypedDict`. However, any `TypedDict` object is
a subtype of (that is, compatible with) `Mapping[str, object]`, since
[`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping "(in Python v3.14)") only provides read-only access to the dictionary items:

```
def print_typed_dict(obj: Mapping[str, object]) -> None:
    for key, value in obj.items():
        print(f'{key}: {value}')

print_typed_dict(Movie(name='Toy Story', year=1995))  # OK
```

Note

Unless you are on Python 3.8 or newer (where `TypedDict` is available in
standard library [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") module) you need to install `typing_extensions`
using pip to use `TypedDict`:

```
python3 -m pip install --upgrade typing-extensions
```

## Totality

By default mypy ensures that a `TypedDict` object has all the specified
keys. This will be flagged as an error:

```
# Error: 'year' missing
toy_story: Movie = {'name': 'Toy Story'}
```

Sometimes you want to allow keys to be left out when creating a
`TypedDict` object. You can provide the `total=False` argument to
`TypedDict(...)` to achieve this:

```
GuiOptions = TypedDict(
    'GuiOptions', {'language': str, 'color': str}, total=False)
options: GuiOptions = {}  # Okay
options['language'] = 'en'
```

You may need to use [`get()`](https://docs.python.org/3/library/stdtypes.html#dict.get "(in Python v3.14)") to access items of a partial (non-total)
`TypedDict`, since indexing using `[]` could fail at runtime.
However, mypy still lets use `[]` with a partial `TypedDict` – you
just need to be careful with it, as it could result in a [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError "(in Python v3.14)").
Requiring [`get()`](https://docs.python.org/3/library/stdtypes.html#dict.get "(in Python v3.14)") everywhere would be too cumbersome. (Note that you
are free to use [`get()`](https://docs.python.org/3/library/stdtypes.html#dict.get "(in Python v3.14)") with total `TypedDict`s as well.)

Keys that aren’t required are shown with a `?` in error messages:

```
# Revealed type is "TypedDict('GuiOptions', {'language'?: builtins.str,
#                                            'color'?: builtins.str})"
reveal_type(options)
```

Totality also affects structural compatibility. You can’t use a partial
`TypedDict` when a total one is expected. Also, a total `TypedDict` is not
valid when a partial one is expected.

## Supported operations

`TypedDict` objects support a subset of dictionary operations and methods.
You must use string literals as keys when calling most of the methods,
as otherwise mypy won’t be able to check that the key is valid. List
of supported operations:

* Anything included in [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping "(in Python v3.14)"):

  + `d[key]`
  + `key in d`
  + `len(d)`
  + `for key in d` (iteration)
  + [`d.get(key[, default])`](https://docs.python.org/3/library/stdtypes.html#dict.get "(in Python v3.14)")
  + [`d.keys()`](https://docs.python.org/3/library/stdtypes.html#dict.keys "(in Python v3.14)")
  + [`d.values()`](https://docs.python.org/3/library/stdtypes.html#dict.values "(in Python v3.14)")
  + [`d.items()`](https://docs.python.org/3/library/stdtypes.html#dict.items "(in Python v3.14)")
* [`d.copy()`](https://docs.python.org/3/library/stdtypes.html#dict.copy "(in Python v3.14)")
* [`d.setdefault(key, default)`](https://docs.python.org/3/library/stdtypes.html#dict.setdefault "(in Python v3.14)")
* [`d1.update(d2)`](https://docs.python.org/3/library/stdtypes.html#dict.update "(in Python v3.14)")
* [`d.pop(key[, default])`](https://docs.python.org/3/library/stdtypes.html#dict.pop "(in Python v3.14)") (partial `TypedDict`s only)
* `del d[key]` (partial `TypedDict`s only)

Note

[`clear()`](https://docs.python.org/3/library/stdtypes.html#dict.clear "(in Python v3.14)") and [`popitem()`](https://docs.python.org/3/library/stdtypes.html#dict.popitem "(in Python v3.14)") are not supported since they are unsafe
– they could delete required `TypedDict` items that are not visible to
mypy because of structural subtyping.

## Class-based syntax

An alternative, class-based syntax to define a `TypedDict` is supported
in Python 3.6 and later:

```
from typing import TypedDict  # "from typing_extensions" in Python 3.7 and earlier

class Movie(TypedDict):
    name: str
    year: int
```

The above definition is equivalent to the original `Movie`
definition. It doesn’t actually define a real class. This syntax also
supports a form of inheritance – subclasses can define additional
items. However, this is primarily a notational shortcut. Since mypy
uses structural compatibility with `TypedDict`s, inheritance is not
required for compatibility. Here is an example of inheritance:

```
class Movie(TypedDict):
    name: str
    year: int

class BookBasedMovie(Movie):
    based_on: str
```

Now `BookBasedMovie` has keys `name`, `year` and `based_on`.

## Mixing required and non-required items

In addition to allowing reuse across `TypedDict` types, inheritance also allows
you to mix required and non-required (using `total=False`) items
in a single `TypedDict`. Example:

```
class MovieBase(TypedDict):
    name: str
    year: int

class Movie(MovieBase, total=False):
    based_on: str
```

Now `Movie` has required keys `name` and `year`, while `based_on`
can be left out when constructing an object. A `TypedDict` with a mix of required
and non-required keys, such as `Movie` above, will only be compatible with
another `TypedDict` if all required keys in the other `TypedDict` are required keys in the
first `TypedDict`, and all non-required keys of the other `TypedDict` are also non-required keys
in the first `TypedDict`.

## Read-only items

You can use `typing.ReadOnly`, introduced in Python 3.13, or
`typing_extensions.ReadOnly` to mark TypedDict items as read-only ([**PEP 705**](https://peps.python.org/pep-0705/)):

```
from typing import TypedDict

# Or "from typing ..." on Python 3.13+
from typing_extensions import ReadOnly

class Movie(TypedDict):
    name: ReadOnly[str]
    num_watched: int

m: Movie = {"name": "Jaws", "num_watched": 1}
m["name"] = "The Godfather"  # Error: "name" is read-only
m["num_watched"] += 1  # OK
```

A TypedDict with a mutable item can be assigned to a TypedDict
with a corresponding read-only item, and the type of the item can
vary [covariantly](generics.html#variance-of-generics):

```
class Entry(TypedDict):
    name: ReadOnly[str | None]
    year: ReadOnly[int]

class Movie(TypedDict):
    name: str
    year: int

def process_entry(i: Entry) -> None: ...

m: Movie = {"name": "Jaws", "year": 1975}
process_entry(m)  # OK
```

## Unions of TypedDicts

Since TypedDicts are really just regular dicts at runtime, it is not possible to
use `isinstance` checks to distinguish between different variants of a Union of
TypedDict in the same way you can with regular objects.

Instead, you can use the [tagged union pattern](literal_types.html#tagged-unions). The referenced
section of the docs has a full description with an example, but in short, you will
need to give each TypedDict the same key where each value has a unique
[Literal type](literal_types.html#literal-types). Then, check that key to distinguish
between your TypedDicts.

## Inline TypedDict types

Note

This is an experimental (non-standard) feature. Use
`--enable-incomplete-feature=InlineTypedDict` to enable.

Sometimes you may want to define a complex nested JSON schema, or annotate
a one-off function that returns a TypedDict. In such cases it may be convenient
to use inline TypedDict syntax. For example:

```
def test_values() -> {"width": int, "description": str}:
    return {"width": 42, "description": "test"}

class Response(TypedDict):
    status: int
    msg: str
    # Using inline syntax here avoids defining two additional TypedDicts.
    content: {"items": list[{"key": str, "value": str}]}
```

Inline TypedDicts can also by used as targets of type aliases, but due to
ambiguity with a regular variables it is only allowed for (newer) explicit
type alias forms:

```
from typing import TypeAlias

X = {"a": int, "b": int}  # creates a variable with type dict[str, type[int]]
Y: TypeAlias = {"a": int, "b": int}  # creates a type alias
type Z = {"a": int, "b": int}  # same as above (Python 3.12+ only)
```

Also, due to incompatibility with runtime type-checking it is strongly recommended
to *not* use inline syntax in union types.