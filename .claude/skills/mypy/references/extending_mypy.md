# Extending and integrating mypy

## Integrating mypy into another Python application

It is possible to integrate mypy into another Python 3 application by
importing `mypy.api` and calling the `run` function with a parameter of type `list[str]`, containing
what normally would have been the command line arguments to mypy.

Function `run` returns a `tuple[str, str, int]`, namely
`(<normal_report>, <error_report>, <exit_status>)`, in which `<normal_report>`
is what mypy normally writes to [`sys.stdout`](https://docs.python.org/3/library/sys.html#sys.stdout "(in Python v3.14)"), `<error_report>` is what mypy
normally writes to [`sys.stderr`](https://docs.python.org/3/library/sys.html#sys.stderr "(in Python v3.14)") and `exit_status` is the exit status mypy normally
returns to the operating system.

A trivial example of using the api is the following

```
import sys
from mypy import api

result = api.run(sys.argv[1:])

if result[0]:
    print('\nType checking report:\n')
    print(result[0])  # stdout

if result[1]:
    print('\nError report:\n')
    print(result[1])  # stderr

print('\nExit status:', result[2])
```

## Extending mypy using plugins

Python is a highly dynamic language and has extensive metaprogramming
capabilities. Many popular libraries use these to create APIs that may
be more flexible and/or natural for humans, but are hard to express using
static types. Extending the [**PEP 484**](https://peps.python.org/pep-0484/) type system to accommodate all existing
dynamic patterns is impractical and often just impossible.

Mypy supports a plugin system that lets you customize the way mypy type checks
code. This can be useful if you want to extend mypy so it can type check code
that uses a library that is difficult to express using just [**PEP 484**](https://peps.python.org/pep-0484/) types.

The plugin system is focused on improving mypy’s understanding
of *semantics* of third party frameworks. There is currently no way to define
new first class kinds of types.

Note

The plugin system is experimental and prone to change. If you want to write
a mypy plugin, we recommend you start by contacting the mypy core developers
on [gitter](https://gitter.im/python/typing). In particular, there are
no guarantees about backwards compatibility.

Backwards incompatible changes may be made without a deprecation period,
but we will announce them in
[the plugin API changes announcement issue](https://github.com/python/mypy/issues/6617).

## Configuring mypy to use plugins

Plugins are Python files that can be specified in a mypy
[config file](config_file.html#config-file) using the [`plugins`](config_file.html#confval-plugins) option and one of the two formats: relative or
absolute path to the plugin file, or a module name (if the plugin
is installed using `pip install` in the same virtual environment where mypy
is running). The two formats can be mixed, for example:

```
[mypy]
plugins = /one/plugin.py, other.plugin
```

Mypy will try to import the plugins and will look for an entry point function
named `plugin`. If the plugin entry point function has a different name, it
can be specified after colon:

```
[mypy]
plugins = custom_plugin:custom_entry_point
```

In the following sections we describe the basics of the plugin system with
some examples. For more technical details, please read the docstrings in
[mypy/plugin.py](https://github.com/python/mypy/blob/master/mypy/plugin.py)
in mypy source code. Also you can find good examples in the bundled plugins
located in [mypy/plugins](https://github.com/python/mypy/tree/master/mypy/plugins).

## High-level overview

Every entry point function should accept a single string argument
that is a full mypy version and return a subclass of `mypy.plugin.Plugin`:

```
from mypy.plugin import Plugin

class CustomPlugin(Plugin):
    def get_type_analyze_hook(self, fullname: str):
        # see explanation below
        ...

def plugin(version: str):
    # ignore version argument if the plugin works with all mypy versions.
    return CustomPlugin
```

During different phases of analyzing the code (first in semantic analysis,
and then in type checking) mypy calls plugin methods such as
`get_type_analyze_hook()` on user plugins. This particular method, for example,
can return a callback that mypy will use to analyze unbound types with the given
full name. See the full plugin hook method list [below](#plugin-hooks).

Mypy maintains a list of plugins it gets from the config file plus the default
(built-in) plugin that is always enabled. Mypy calls a method once for each
plugin in the list until one of the methods returns a non-`None` value.
This callback will be then used to customize the corresponding aspect of
analyzing/checking the current abstract syntax tree node.

The callback returned by the `get_xxx` method will be given a detailed
current context and an API to create new nodes, new types, emit error messages,
etc., and the result will be used for further processing.

Plugin developers should ensure that their plugins work well in incremental and
daemon modes. In particular, plugins should not hold global state due to caching
of plugin hook results.

## Current list of plugin hooks

**get\_type\_analyze\_hook()** customizes behaviour of the type analyzer.
For example, [**PEP 484**](https://peps.python.org/pep-0484/) doesn’t support defining variadic generic types:

```
from lib import Vector

a: Vector[int, int]
b: Vector[int, int, int]
```

When analyzing this code, mypy will call `get_type_analyze_hook("lib.Vector")`,
so the plugin can return some valid type for each variable.

**get\_function\_hook()** is used to adjust the return type of a function call.
This hook will be also called for instantiation of classes.
This is a good choice if the return type is too complex
to be expressed by regular python typing.

**get\_function\_signature\_hook()** is used to adjust the signature of a function.

**get\_method\_hook()** is the same as `get_function_hook()` but for methods
instead of module level functions.

**get\_method\_signature\_hook()** is used to adjust the signature of a method.
This includes special Python methods except [`__init__()`](https://docs.python.org/3/reference/datamodel.html#object.__init__ "(in Python v3.14)") and [`__new__()`](https://docs.python.org/3/reference/datamodel.html#object.__new__ "(in Python v3.14)").
For example in this code:

```
from ctypes import Array, c_int

x: Array[c_int]
x[0] = 42
```

mypy will call `get_method_signature_hook("ctypes.Array.__setitem__")`
so that the plugin can mimic the [`ctypes`](https://docs.python.org/3/library/ctypes.html#module-ctypes "(in Python v3.14)") auto-convert behavior.

**get\_attribute\_hook()** overrides instance member field lookups and property
access (not method calls). This hook is only called for
fields which already exist on the class. *Exception:* if [`__getattr__`](https://docs.python.org/3/reference/datamodel.html#object.__getattr__ "(in Python v3.14)") or
[`__getattribute__`](https://docs.python.org/3/reference/datamodel.html#object.__getattribute__ "(in Python v3.14)") is a method on the class, the hook is called for all
fields which do not refer to methods.

**get\_class\_attribute\_hook()** is similar to above, but for attributes on classes rather than instances.
Unlike above, this does not have special casing for [`__getattr__`](https://docs.python.org/3/reference/datamodel.html#object.__getattr__ "(in Python v3.14)") or
[`__getattribute__`](https://docs.python.org/3/reference/datamodel.html#object.__getattribute__ "(in Python v3.14)").

**get\_class\_decorator\_hook()** can be used to update class definition for
given class decorators. For example, you can add some attributes to the class
to match runtime behaviour:

```
from dataclasses import dataclass

@dataclass  # built-in plugin adds `__init__` method here
class User:
    name: str

user = User(name='example')  # mypy can understand this using a plugin
```

**get\_metaclass\_hook()** is similar to above, but for metaclasses.

**get\_base\_class\_hook()** is similar to above, but for base classes.

**get\_dynamic\_class\_hook()** can be used to allow dynamic class definitions
in mypy. This plugin hook is called for every assignment to a simple name
where right hand side is a function call:

```
from lib import dynamic_class

X = dynamic_class('X', [])
```

For such definition, mypy will call `get_dynamic_class_hook("lib.dynamic_class")`.
The plugin should create the corresponding `mypy.nodes.TypeInfo` object, and
place it into a relevant symbol table. (Instances of this class represent
classes in mypy and hold essential information such as qualified name,
method resolution order, etc.)

**get\_customize\_class\_mro\_hook()** can be used to modify class MRO (for example
insert some entries there) before the class body is analyzed.

**get\_additional\_deps()** can be used to add new dependencies for a
module. It is called before semantic analysis. For example, this can
be used if a library has dependencies that are dynamically loaded
based on configuration information.

**report\_config\_data()** can be used if the plugin has some sort of
per-module configuration that can affect typechecking. In that case,
when the configuration for a module changes, we want to invalidate
mypy’s cache for that module so that it can be rechecked. This hook
should be used to report to mypy any relevant configuration data,
so that mypy knows to recheck the module if the configuration changes.
The hooks should return data encodable as JSON.

## Useful tools

Mypy ships `mypy.plugins.proper_plugin` plugin which can be useful
for plugin authors, since it finds missing `get_proper_type()` calls,
which is a pretty common mistake.

It is recommended to enable it as a part of your plugin’s CI.