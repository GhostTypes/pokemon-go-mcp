# The mypy command line

This section documents mypy’s command line interface. You can view
a quick summary of the available flags by running [`mypy --help`](#cmdoption-mypy-h).

Note

Command line flags are liable to change between releases.

## Specifying what to type check

By default, you can specify what code you want mypy to type check
by passing in the paths to what you want to have type checked:

```
$ mypy foo.py bar.py some_directory
```

Note that directories are checked recursively.

Mypy also lets you specify what code to type check in several other
ways. A short summary of the relevant flags is included below:
for full details, see [Running mypy and managing imports](running_mypy.html#running-mypy).

-m MODULE, --module MODULE
:   Asks mypy to type check the provided module. This flag may be
    repeated multiple times.

    Mypy *will not* recursively type check any submodules of the provided
    module.

-p PACKAGE, --package PACKAGE
:   Asks mypy to type check the provided package. This flag may be
    repeated multiple times.

    Mypy *will* recursively type check any submodules of the provided
    package. This flag is identical to [`--module`](#cmdoption-mypy-m) apart from this
    behavior.

-c PROGRAM\_TEXT, --command PROGRAM\_TEXT
:   Asks mypy to type check the provided string as a program.

--exclude
:   A regular expression that matches file names, directory names and paths
    which mypy should ignore while recursively discovering files to check.
    Use forward slashes on all platforms.

    For instance, to avoid discovering any files named setup.py you could
    pass `--exclude '/setup\.py$'`. Similarly, you can ignore discovering
    directories with a given name by e.g. `--exclude /build/` or
    those matching a subpath with `--exclude /project/vendor/`. To ignore
    multiple files / directories / paths, you can provide the –exclude
    flag more than once, e.g `--exclude '/setup\.py$' --exclude '/build/'`.

    Note that this flag only affects recursive directory tree discovery, that
    is, when mypy is discovering files within a directory tree or submodules of
    a package to check. If you pass a file or module explicitly it will still be
    checked. For instance, `mypy --exclude '/setup.py$'
    but_still_check/setup.py`.

    In particular, `--exclude` does not affect mypy’s discovery of files
    via [import following](running_mypy.html#follow-imports). You can use a per-module
    [`ignore_errors`](config_file.html#confval-ignore_errors) config option to silence errors from a given module,
    or a per-module [`follow_imports`](config_file.html#confval-follow_imports) config option to additionally avoid
    mypy from following imports and checking code you do not wish to be checked.

    Note that mypy will never recursively discover files and directories named
    “site-packages”, “node\_modules” or “\_\_pycache\_\_”, or those whose name starts
    with a period, exactly as `--exclude
    '/(site-packages|node_modules|__pycache__|\..*)/$'` would. Mypy will also
    never recursively discover files with extensions other than `.py` or
    `.pyi`.

--exclude-gitignore
:   This flag will add everything that matches `.gitignore` file(s) to [`--exclude`](#cmdoption-mypy-exclude).

## Optional arguments

-h, --help
:   Show help message and exit.

-v, --verbose
:   More verbose messages.

-V, --version
:   Show program’s version number and exit.

-O FORMAT, --output FORMAT {json}
:   Set a custom output format.

## Config file

--config-file CONFIG\_FILE
:   This flag makes mypy read configuration settings from the given file.

    By default settings are read from `mypy.ini`, `.mypy.ini`, `pyproject.toml`, or `setup.cfg`
    in the current directory. Settings override mypy’s built-in defaults and
    command line flags can override settings.

    Specifying [`--config-file=`](#cmdoption-mypy-config-file) (with no filename) will ignore *all*
    config files.

    See [The mypy configuration file](config_file.html#config-file) for the syntax of configuration files.

--warn-unused-configs
:   This flag makes mypy warn about unused `[mypy-<pattern>]` config
    file sections.
    (This requires turning off incremental mode using [`--no-incremental`](#cmdoption-mypy-no-incremental).)

## Import discovery

The following flags customize how exactly mypy discovers and follows
imports.

--explicit-package-bases
:   This flag tells mypy that top-level packages will be based in either the
    current directory, or a member of the `MYPYPATH` environment variable or
    [`mypy_path`](config_file.html#confval-mypy_path) config option. This option is only useful
    in the absence of \_\_init\_\_.py. See [Mapping file
    paths to modules](running_mypy.html#mapping-paths-to-modules) for details.

--ignore-missing-imports
:   This flag makes mypy ignore all missing imports. It is equivalent
    to adding `# type: ignore` comments to all unresolved imports
    within your codebase.

    Note that this flag does *not* suppress errors about missing names
    in successfully resolved modules. For example, if one has the
    following files:

    ```
    package/__init__.py
    package/mod.py
    ```

    Then mypy will generate the following errors with [`--ignore-missing-imports`](#cmdoption-mypy-ignore-missing-imports):

    ```
    import package.unknown      # No error, ignored
    x = package.unknown.func()  # OK. 'func' is assumed to be of type 'Any'

    from package import unknown          # No error, ignored
    from package.mod import NonExisting  # Error: Module has no attribute 'NonExisting'
    ```

    For more details, see [Missing imports](running_mypy.html#ignore-missing-imports).

--follow-untyped-imports
:   This flag makes mypy analyze imports from installed packages even if
    missing a [py.typed marker or stubs](installed_packages.html#installed-packages).

    Warning

    Note that analyzing all unannotated modules might result in issues
    when analyzing code not designed to be type checked and may significantly
    increase how long mypy takes to run.

--follow-imports {normal,silent,skip,error}
:   This flag adjusts how mypy follows imported modules that were not
    explicitly passed in via the command line.

    The default option is `normal`: mypy will follow and type check
    all modules. For more information on what the other options do,
    see [Following imports](running_mypy.html#follow-imports).

--python-executable EXECUTABLE
:   This flag will have mypy collect type information from [**PEP 561**](https://peps.python.org/pep-0561/)
    compliant packages installed for the Python executable `EXECUTABLE`.
    If not provided, mypy will use PEP 561 compliant packages installed for
    the Python executable running mypy.

    See [Using installed packages](installed_packages.html#installed-packages) for more on making PEP 561 compliant packages.

--no-site-packages
:   This flag will disable searching for [**PEP 561**](https://peps.python.org/pep-0561/) compliant packages. This
    will also disable searching for a usable Python executable.

    Use this flag if mypy cannot find a Python executable for the version of
    Python being checked, and you don’t need to use PEP 561 typed packages.
    Otherwise, use [`--python-executable`](#cmdoption-mypy-python-executable).

--no-silence-site-packages
:   By default, mypy will suppress any error messages generated within [**PEP 561**](https://peps.python.org/pep-0561/)
    compliant packages. Adding this flag will disable this behavior.

--fast-module-lookup
:   The default logic used to scan through search paths to resolve imports has a
    quadratic worse-case behavior in some cases, which is for instance triggered
    by a large number of folders sharing a top-level namespace as in:

    ```
    foo/
        company/
            foo/
                a.py
    bar/
        company/
            bar/
                b.py
    baz/
        company/
            baz/
                c.py
    ...
    ```

    If you are in this situation, you can enable an experimental fast path by
    setting the [`--fast-module-lookup`](#cmdoption-mypy-fast-module-lookup) option.

--no-namespace-packages
:   This flag disables import discovery of namespace packages (see [**PEP 420**](https://peps.python.org/pep-0420/)).
    In particular, this prevents discovery of packages that don’t have an
    `__init__.py` (or `__init__.pyi`) file.

    This flag affects how mypy finds modules and packages explicitly passed on
    the command line. It also affects how mypy determines fully qualified module
    names for files passed on the command line. See [Mapping file paths to
    modules](running_mypy.html#mapping-paths-to-modules) for details.

## Platform configuration

By default, mypy will assume that you intend to run your code using the same
operating system and Python version you are using to run mypy itself. The
following flags let you modify this behavior.

For more information on how to use these flags, see [Python version and system platform checks](common_issues.html#version-and-platform-checks).

--python-version X.Y
:   This flag will make mypy type check your code as if it were
    run under Python version X.Y. Without this option, mypy will default to using
    whatever version of Python is running mypy.

    This flag will attempt to find a Python executable of the corresponding
    version to search for [**PEP 561**](https://peps.python.org/pep-0561/) compliant packages. If you’d like to
    disable this, use the [`--no-site-packages`](#cmdoption-mypy-no-site-packages) flag (see
    [Import discovery](#import-discovery) for more details).

--platform PLATFORM
:   This flag will make mypy type check your code as if it were
    run under the given operating system. Without this option, mypy will
    default to using whatever operating system you are currently using.

    The `PLATFORM` parameter may be any string supported by
    [`sys.platform`](https://docs.python.org/3/library/sys.html#sys.platform "(in Python v3.14)").

--always-true NAME
:   This flag will treat all variables named `NAME` as
    compile-time constants that are always true. This flag may
    be repeated.

--always-false NAME
:   This flag will treat all variables named `NAME` as
    compile-time constants that are always false. This flag may
    be repeated.

## Disallow dynamic typing

The `Any` type is used to represent a value that has a [dynamic type](dynamic_typing.html#dynamic-typing).
The `--disallow-any` family of flags will disallow various uses of the `Any` type in
a module – this lets us strategically disallow the use of dynamic typing in a controlled way.

The following options are available:

--disallow-any-unimported
:   This flag disallows usage of types that come from unfollowed imports
    (such types become aliases for `Any`). Unfollowed imports occur either
    when the imported module does not exist or when [`--follow-imports=skip`](#cmdoption-mypy-follow-imports)
    is set.

--disallow-any-expr
:   This flag disallows all expressions in the module that have type `Any`.
    If an expression of type `Any` appears anywhere in the module
    mypy will output an error unless the expression is immediately
    used as an argument to [`cast()`](https://docs.python.org/3/library/typing.html#typing.cast "(in Python v3.14)") or assigned to a variable with an
    explicit type annotation.

    In addition, declaring a variable of type `Any`
    or casting to type `Any` is not allowed. Note that calling functions
    that take parameters of type `Any` is still allowed.

--disallow-any-decorated
:   This flag disallows functions that have `Any` in their signature
    after decorator transformation.

--disallow-any-explicit
:   This flag disallows explicit `Any` in type positions such as type
    annotations and generic type parameters.

--disallow-any-generics
:   This flag disallows usage of generic types that do not specify explicit
    type parameters. For example, you can’t use a bare `x: list`. Instead, you
    must always write something like `x: list[int]`.

--disallow-subclassing-any
:   This flag reports an error whenever a class subclasses a value of
    type `Any`. This may occur when the base class is imported from
    a module that doesn’t exist (when using
    [`--ignore-missing-imports`](#cmdoption-mypy-ignore-missing-imports)) or is
    ignored due to [`--follow-imports=skip`](#cmdoption-mypy-follow-imports) or a
    `# type: ignore` comment on the `import` statement.

    Since the module is silenced, the imported class is given a type of `Any`.
    By default mypy will assume that the subclass correctly inherited
    the base class even though that may not actually be the case. This
    flag makes mypy raise an error instead.

## Untyped definitions and calls

The following flags configure how mypy handles untyped function
definitions or calls.

--disallow-untyped-calls
:   This flag reports an error whenever a function with type annotations
    calls a function defined without annotations.

--untyped-calls-exclude
:   This flag allows one to selectively disable [`--disallow-untyped-calls`](#cmdoption-mypy-disallow-untyped-calls)
    for functions and methods defined in specific packages, modules, or classes.
    Note that each exclude entry acts as a prefix. For example (assuming there
    are no type annotations for `third_party_lib` available):

    ```
    # mypy --disallow-untyped-calls
    #      --untyped-calls-exclude=third_party_lib.module_a
    #      --untyped-calls-exclude=foo.A
    from third_party_lib.module_a import some_func
    from third_party_lib.module_b import other_func
    import foo

    some_func()  # OK, function comes from module `third_party_lib.module_a`
    other_func()  # E: Call to untyped function "other_func" in typed context

    foo.A().meth()  # OK, method was defined in class `foo.A`
    foo.B().meth()  # E: Call to untyped function "meth" in typed context

    # file foo.py
    class A:
        def meth(self): pass
    class B:
        def meth(self): pass
    ```

--disallow-untyped-defs
:   This flag reports an error whenever it encounters a function definition
    without type annotations or with incomplete type annotations.
    (a superset of [`--disallow-incomplete-defs`](#cmdoption-mypy-disallow-incomplete-defs)).

    For example, it would report an error for `def f(a, b)` and `def f(a: int, b)`.

--disallow-incomplete-defs
:   This flag reports an error whenever it encounters a partly annotated
    function definition, while still allowing entirely unannotated definitions.

    For example, it would report an error for `def f(a: int, b)` but not `def f(a, b)`.

--check-untyped-defs
:   This flag is less severe than the previous two options – it type checks
    the body of every function, regardless of whether it has type annotations.
    (By default the bodies of functions without annotations are not type
    checked.)

    It will assume all arguments have type `Any` and always infer `Any`
    as the return type.

--disallow-untyped-decorators
:   This flag reports an error whenever a function with type annotations
    is decorated with a decorator without annotations.

## None and Optional handling

The following flags adjust how mypy handles values of type `None`.

--implicit-optional
:   This flag causes mypy to treat parameters with a `None`
    default value as having an implicit optional type (`T | None`).

    For example, if this flag is set, mypy would assume that the `x`
    parameter is actually of type `int | None` in the code snippet below,
    since the default parameter is `None`:

    ```
    def foo(x: int = None) -> None:
        print(x)
    ```

    **Note:** This was disabled by default starting in mypy 0.980.

--no-strict-optional
:   This flag effectively disables checking of optional
    types and `None` values. With this option, mypy doesn’t
    generally check the use of `None` values – it is treated
    as compatible with every type.

    Warning

    `--no-strict-optional` is evil. Avoid using it and definitely do
    not use it without understanding what it does.

## Configuring warnings

The following flags enable warnings for code that is sound but is
potentially problematic or redundant in some way.

--warn-redundant-casts
:   This flag will make mypy report an error whenever your code uses
    an unnecessary cast that can safely be removed.

--warn-unused-ignores
:   This flag will make mypy report an error whenever your code uses
    a `# type: ignore` comment on a line that is not actually
    generating an error message.

    This flag, along with the [`--warn-redundant-casts`](#cmdoption-mypy-warn-redundant-casts) flag, are both
    particularly useful when you are upgrading mypy. Previously,
    you may have needed to add casts or `# type: ignore` annotations
    to work around bugs in mypy or missing stubs for 3rd party libraries.

    These two flags let you discover cases where either workarounds are
    no longer necessary.

--no-warn-no-return
:   By default, mypy will generate errors when a function is missing
    return statements in some execution paths. The only exceptions
    are when:

    * The function has a `None` or `Any` return type
    * The function has an empty body and is marked as an abstract method,
      is in a protocol class, or is in a stub file
    * The execution path can never return; for example, if an exception
      :   is always raised

    Passing in [`--no-warn-no-return`](#cmdoption-mypy-no-warn-no-return) will disable these error
    messages in all cases.

--warn-return-any
:   This flag causes mypy to generate a warning when returning a value
    with type `Any` from a function declared with a non-`Any` return type.

--warn-unreachable
:   This flag will make mypy report an error whenever it encounters
    code determined to be unreachable or redundant after performing type analysis.
    This can be a helpful way of detecting certain kinds of bugs in your code.

    For example, enabling this flag will make mypy report that the `x > 7`
    check is redundant and that the `else` block below is unreachable.

    ```
    def process(x: int) -> None:
        # Error: Right operand of "or" is never evaluated
        if isinstance(x, int) or x > 7:
            # Error: Unsupported operand types for + ("int" and "str")
            print(x + "bad")
        else:
            # Error: 'Statement is unreachable' error
            print(x + "bad")
    ```

    To help prevent mypy from generating spurious warnings, the “Statement is
    unreachable” warning will be silenced in exactly two cases:

    1. When the unreachable statement is a `raise` statement, is an
       `assert False` statement, or calls a function that has the [`NoReturn`](https://docs.python.org/3/library/typing.html#typing.NoReturn "(in Python v3.14)")
       return type hint. In other words, when the unreachable statement
       throws an error or terminates the program in some way.
    2. When the unreachable statement was *intentionally* marked as unreachable
       using [Python version and system platform checks](common_issues.html#version-and-platform-checks).

    Note

    Mypy currently cannot detect and report unreachable or redundant code
    inside any functions using [Type variables with value restriction](generics.html#type-variable-value-restriction).

    This limitation will be removed in future releases of mypy.

--report-deprecated-as-note
:   If error code `deprecated` is enabled, mypy emits errors if your code
    imports or uses deprecated features. This flag converts such errors to
    notes, causing mypy to eventually finish with a zero exit code. Features
    are considered deprecated when decorated with `warnings.deprecated`.

--deprecated-calls-exclude
:   This flag allows one to selectively disable [deprecated](error_code_list2.html#code-deprecated) warnings
    for functions and methods defined in specific packages, modules, or classes.
    Note that each exclude entry acts as a prefix. For example (assuming `foo.A.func` is deprecated):

    ```
    # mypy --enable-error-code deprecated
    #      --deprecated-calls-exclude=foo.A
    import foo

    foo.A().func()  # OK, the deprecated warning is ignored

    # file foo.py
    from typing_extensions import deprecated
    class A:
        @deprecated("Use A.func2 instead")
        def func(self): pass
    ```

## Miscellaneous strictness flags

This section documents any other flags that do not neatly fall under any
of the above sections.

--allow-untyped-globals
:   This flag causes mypy to suppress errors caused by not being able to fully
    infer the types of global and class variables.

--allow-redefinition-new
:   By default, mypy won’t allow a variable to be redefined with an
    unrelated type. This *experimental* flag enables the redefinition of
    unannotated variables with an arbitrary type. You will also need to enable
    [`--local-partial-types`](#cmdoption-mypy-local-partial-types).
    Example:

    ```
    def maybe_convert(n: int, b: bool) -> int | str:
        if b:
            x = str(n)  # Assign "str"
        else:
            x = n       # Assign "int"
        # Type of "x" is "int | str" here.
        return x
    ```

    Without the new flag, mypy only supports inferring optional types
    (`X | None`) from multiple assignments. With this option enabled,
    mypy can infer arbitrary union types.

    This also enables an unannotated variable to have different types in different
    code locations:

    ```
    if check():
        for x in range(n):
            # Type of "x" is "int" here.
            ...
    else:
        for x in ['a', 'b']:
            # Type of "x" is "str" here.
            ...
    ```

    Note: We are planning to turn this flag on by default in a future mypy
    release, along with [`--local-partial-types`](#cmdoption-mypy-local-partial-types).
    The feature is still experimental, and the semantics may still change.

--allow-redefinition
:   This is an older variant of
    [`--allow-redefinition-new`](#cmdoption-mypy-allow-redefinition-new).
    This flag enables redefinition of a variable with an
    arbitrary type *in some contexts*: only redefinitions within the
    same block and nesting depth as the original definition are allowed.

    We have no plans to remove this flag, but we expect that
    [`--allow-redefinition-new`](#cmdoption-mypy-allow-redefinition-new)
    will replace this flag for new use cases eventually.

    Example where this can be useful:

    ```
    def process(items: list[str]) -> None:
        # 'items' has type list[str]
        items = [item.split() for item in items]
        # 'items' now has type list[list[str]]
    ```

    The variable must be used before it can be redefined:

    ```
    def process(items: list[str]) -> None:
       items = "mypy"  # invalid redefinition to str because the variable hasn't been used yet
       print(items)
       items = "100"  # valid, items now has type str
       items = int(items)  # valid, items now has type int
    ```

--local-partial-types
:   In mypy, the most common cases for partial types are variables initialized using `None`,
    but without explicit `X | None` annotations. By default, mypy won’t check partial types
    spanning module top level or class top level. This flag changes the behavior to only allow
    partial types at local level, therefore it disallows inferring variable type for `None`
    from two assignments in different scopes. For example:

    ```
    a = None  # Need type annotation here if using --local-partial-types
    b: int | None = None

    class Foo:
        bar = None  # Need type annotation here if using --local-partial-types
        baz: int | None = None

        def __init__(self) -> None:
            self.bar = 1

    reveal_type(Foo().bar)  # 'int | None' without --local-partial-types
    ```

    Note: this option is always implicitly enabled in mypy daemon and will become
    enabled by default for mypy in a future release.

--no-implicit-reexport
:   By default, imported values to a module are treated as exported and mypy allows
    other modules to import them. This flag changes the behavior to not re-export unless
    the item is imported using from-as or is included in `__all__`. Note this is
    always treated as enabled for stub files. For example:

    ```
    # This won't re-export the value
    from foo import bar

    # Neither will this
    from foo import bar as bang

    # This will re-export it as bar and allow other modules to import it
    from foo import bar as bar

    # This will also re-export bar
    from foo import bar
    __all__ = ['bar']
    ```

--strict-equality
:   By default, mypy allows always-false comparisons like `42 == 'no'`.
    Use this flag to prohibit such comparisons of non-overlapping types, and
    similar identity and container checks:

    ```
    items: list[int]
    if 'some string' in items:  # Error: non-overlapping container check!
        ...

    text: str
    if text != b'other bytes':  # Error: non-overlapping equality check!
        ...

    assert text is not None  # OK, check against None is allowed
    ```

--strict-equality-for-none
:   This flag extends [`--strict-equality`](#cmdoption-mypy-strict-equality) for checks
    against `None`:

    ```
    text: str
    assert text is not None  # Error: non-overlapping identity check!
    ```

    Note that [`--strict-equality-for-none`](#cmdoption-mypy-strict-equality-for-none)
    only works in combination with [`--strict-equality`](#cmdoption-mypy-strict-equality).

--strict-bytes
:   By default, mypy treats `bytearray` and `memoryview` as subtypes of `bytes` which
    is not true at runtime. Use this flag to disable this behavior. `--strict-bytes` will
    be enabled by default in *mypy 2.0*.

    ```
    def f(buf: bytes) -> None:
        assert isinstance(buf, bytes)  # Raises runtime AssertionError with bytearray/memoryview
        with open("binary_file", "wb") as fp:
            fp.write(buf)

    f(bytearray(b""))  # error: Argument 1 to "f" has incompatible type "bytearray"; expected "bytes"
    f(memoryview(b""))  # error: Argument 1 to "f" has incompatible type "memoryview"; expected "bytes"

    # If `f` accepts any object that implements the buffer protocol, consider using:
    from collections.abc import Buffer  # "from typing_extensions" in Python 3.11 and earlier

    def f(buf: Buffer) -> None:
        with open("binary_file", "wb") as fp:
            fp.write(buf)

    f(b"")  # Ok
    f(bytearray(b""))  # Ok
    f(memoryview(b""))  # Ok
    ```

--extra-checks
:   This flag enables additional checks that are technically correct but may be
    impractical. In particular, it prohibits partial overlap in `TypedDict` updates,
    and makes arguments prepended via `Concatenate` positional-only. For example:

    ```
    from typing import TypedDict

    class Foo(TypedDict):
        a: int

    class Bar(TypedDict):
        a: int
        b: int

    def test(foo: Foo, bar: Bar) -> None:
        # This is technically unsafe since foo can have a subtype of Foo at
        # runtime, where type of key "b" is incompatible with int, see below
        bar.update(foo)

    class Bad(Foo):
        b: str
    bad: Bad = {"a": 0, "b": "no"}
    test(bad, bar)
    ```

    In future more checks may be added to this flag if:

    * The corresponding use cases are rare, thus not justifying a dedicated
      strictness flag.
    * The new check cannot be supported as an opt-in error code.

--strict
:   This flag mode enables a defined subset of optional error-checking flags.
    This subset primarily includes checks for inadvertent type unsoundness (i.e
    strict will catch type errors as long as intentional methods like type ignore
    or casting were not used.)

    Note: the [`--warn-unreachable`](#cmdoption-mypy-warn-unreachable) flag
    is not automatically enabled by the strict flag.

    The strict flag does not take precedence over other strict-related flags.
    Directly specifying a flag of alternate behavior will override the
    behavior of strict, regardless of the order in which they are passed.
    You can see the list of flags enabled by strict mode in the full
    [`mypy --help`](#cmdoption-mypy-h) output.

    Note: the exact list of flags enabled by running [`--strict`](#cmdoption-mypy-strict) may change
    over time.

    For this version of mypy, the list of flags enabled by strict is: [`--warn-unused-configs`](#cmdoption-mypy-warn-unused-configs), [`--disallow-any-generics`](#cmdoption-mypy-disallow-any-generics), [`--disallow-subclassing-any`](#cmdoption-mypy-disallow-subclassing-any), [`--disallow-untyped-calls`](#cmdoption-mypy-disallow-untyped-calls), [`--disallow-untyped-defs`](#cmdoption-mypy-disallow-untyped-defs), [`--disallow-incomplete-defs`](#cmdoption-mypy-disallow-incomplete-defs), [`--check-untyped-defs`](#cmdoption-mypy-check-untyped-defs), [`--disallow-untyped-decorators`](#cmdoption-mypy-disallow-untyped-decorators), [`--warn-redundant-casts`](#cmdoption-mypy-warn-redundant-casts), [`--warn-unused-ignores`](#cmdoption-mypy-warn-unused-ignores), [`--warn-return-any`](#cmdoption-mypy-warn-return-any), [`--no-implicit-reexport`](#cmdoption-mypy-no-implicit-reexport), [`--strict-equality`](#cmdoption-mypy-strict-equality), [`--strict-bytes`](#cmdoption-mypy-strict-bytes), [`--extra-checks`](#cmdoption-mypy-extra-checks)

--disable-error-code
:   This flag allows disabling one or multiple error codes globally.
    See [Error codes](error_codes.html#error-codes) for more information.

    ```
    # no flag
    x = 'a string'
    x.trim()  # error: "str" has no attribute "trim"  [attr-defined]

    # When using --disable-error-code attr-defined
    x = 'a string'
    x.trim()
    ```

--enable-error-code
:   This flag allows enabling one or multiple error codes globally.
    See [Error codes](error_codes.html#error-codes) for more information.

    Note: This flag will override disabled error codes from the
    [`--disable-error-code`](#cmdoption-mypy-disable-error-code) flag.

    ```
    # When using --disable-error-code attr-defined
    x = 'a string'
    x.trim()

    # --disable-error-code attr-defined --enable-error-code attr-defined
    x = 'a string'
    x.trim()  # error: "str" has no attribute "trim"  [attr-defined]
    ```

## Configuring error messages

The following flags let you adjust how much detail mypy displays
in error messages.

--show-error-context
:   This flag will precede all errors with “note” messages explaining the
    context of the error. For example, consider the following program:

    ```
    class Test:
        def foo(self, x: int) -> int:
            return x + "bar"
    ```

    Mypy normally displays an error message that looks like this:

    ```
    main.py:3: error: Unsupported operand types for + ("int" and "str")
    ```

    If we enable this flag, the error message now looks like this:

    ```
    main.py: note: In member "foo" of class "Test":
    main.py:3: error: Unsupported operand types for + ("int" and "str")
    ```

--show-column-numbers
:   This flag will add column offsets to error messages.
    For example, the following indicates an error in line 12, column 9
    (note that column offsets are 0-based):

    ```
    main.py:12:9: error: Unsupported operand types for / ("int" and "str")
    ```

--show-error-code-links
:   This flag will also display a link to error code documentation, anchored to the error code reported by mypy.
    The corresponding error code will be highlighted within the documentation page.
    If we enable this flag, the error message now looks like this:

    ```
    main.py:3: error: Unsupported operand types for - ("int" and "str")  [operator]
    main.py:3: note: See 'https://mypy.rtfd.io/en/stable/_refs.html#code-operator' for more info
    ```

--show-error-end
:   This flag will make mypy show not just that start position where
    an error was detected, but also the end position of the relevant expression.
    This way various tools can easily highlight the whole error span. The format is
    `file:line:column:end_line:end_column`. This option implies
    `--show-column-numbers`.

--hide-error-codes
:   This flag will hide the error code `[<code>]` from error messages. By default, the error
    code is shown after each error message:

    ```
    prog.py:1: error: "str" has no attribute "trim"  [attr-defined]
    ```

    See [Error codes](error_codes.html#error-codes) for more information.

--pretty
:   Use visually nicer output in error messages: use soft word wrap,
    show source code snippets, and show error location markers.

--no-color-output
:   This flag will disable color output in error messages, enabled by default.

--no-error-summary
:   This flag will disable error summary. By default mypy shows a summary line
    including total number of errors, number of files with errors, and number
    of files checked.

--show-absolute-path
:   Show absolute paths to files.

--soft-error-limit N
:   This flag will adjust the limit after which mypy will (sometimes)
    disable reporting most additional errors. The limit only applies
    if it seems likely that most of the remaining errors will not be
    useful or they may be overly noisy. If `N` is negative, there is
    no limit. The default limit is -1.

--force-union-syntax
:   Always use `Union[]` and `Optional[]` for union types
    in error messages (instead of the `|` operator),
    even on Python 3.10+.

## Incremental mode

By default, mypy will store type information into a cache. Mypy
will use this information to avoid unnecessary recomputation when
it type checks your code again. This can help speed up the type
checking process, especially when most parts of your program have
not changed since the previous mypy run.

If you want to speed up how long it takes to recheck your code
beyond what incremental mode can offer, try running mypy in
[daemon mode](mypy_daemon.html#mypy-daemon).

--no-incremental
:   This flag disables incremental mode: mypy will no longer reference
    the cache when re-run.

    Note that mypy will still write out to the cache even when
    incremental mode is disabled: see the [`--cache-dir`](#cmdoption-mypy-cache-dir) flag below
    for more details.

--cache-dir DIR
:   By default, mypy stores all cache data inside of a folder named
    `.mypy_cache` in the current directory. This flag lets you
    change this folder. This flag can also be useful for controlling
    cache use when using [remote caching](additional_features.html#remote-cache).

    This setting will override the `MYPY_CACHE_DIR` environment
    variable if it is set.

    Mypy will also always write to the cache even when incremental
    mode is disabled so it can “warm up” the cache. To disable
    writing to the cache, use `--cache-dir=/dev/null` (UNIX)
    or `--cache-dir=nul` (Windows).

--sqlite-cache
:   Use an [SQLite](https://www.sqlite.org/) database to store the cache.

--cache-fine-grained
:   Include fine-grained dependency information in the cache for the mypy daemon.

--skip-version-check
:   By default, mypy will ignore cache data generated by a different
    version of mypy. This flag disables that behavior.

--skip-cache-mtime-checks
:   Skip cache internal consistency checks based on mtime.

## Advanced options

The following flags are useful mostly for people who are interested
in developing or debugging mypy internals.

--pdb
:   This flag will invoke the Python debugger when mypy encounters
    a fatal error.

--show-traceback, --tb
:   If set, this flag will display a full traceback when mypy
    encounters a fatal error.

--raise-exceptions
:   Raise exception on fatal error.

--custom-typing-module MODULE
:   This flag lets you use a custom module as a substitute for the
    [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") module.

--custom-typeshed-dir DIR
:   This flag specifies the directory where mypy looks for standard library typeshed
    stubs, instead of the typeshed that ships with mypy. This is
    primarily intended to make it easier to test typeshed changes before
    submitting them upstream, but also allows you to use a forked version of
    typeshed.

    Note that this doesn’t affect third-party library stubs. To test third-party stubs,
    for example try `MYPYPATH=stubs/six mypy ...`.

--warn-incomplete-stub
:   This flag modifies both the [`--disallow-untyped-defs`](#cmdoption-mypy-disallow-untyped-defs) and
    [`--disallow-incomplete-defs`](#cmdoption-mypy-disallow-incomplete-defs) flags so they also report errors
    if stubs in typeshed are missing type annotations or has incomplete
    annotations. If both flags are missing, [`--warn-incomplete-stub`](#cmdoption-mypy-warn-incomplete-stub)
    also does nothing.

    This flag is mainly intended to be used by people who want contribute
    to typeshed and would like a convenient way to find gaps and omissions.

    If you want mypy to report an error when your codebase *uses* an untyped
    function, whether that function is defined in typeshed or not, use the
    [`--disallow-untyped-calls`](#cmdoption-mypy-disallow-untyped-calls) flag. See [Untyped definitions and calls](#untyped-definitions-and-calls)
    for more details.

--shadow-file SOURCE\_FILE SHADOW\_FILE
:   When mypy is asked to type check `SOURCE_FILE`, this flag makes mypy
    read from and type check the contents of `SHADOW_FILE` instead. However,
    diagnostics will continue to refer to `SOURCE_FILE`.

    Specifying this argument multiple times (`--shadow-file X1 Y1 --shadow-file X2 Y2`)
    will allow mypy to perform multiple substitutions.

    This allows tooling to create temporary files with helpful modifications
    without having to change the source file in place. For example, suppose we
    have a pipeline that adds `reveal_type` for certain variables.
    This pipeline is run on `original.py` to produce `temp.py`.
    Running `mypy --shadow-file original.py temp.py original.py` will then
    cause mypy to type check the contents of `temp.py` instead of `original.py`,
    but error messages will still reference `original.py`.

## Report generation

If these flags are set, mypy will generate a report in the specified
format into the specified directory.

--any-exprs-report DIR
:   Causes mypy to generate a text file report documenting how many
    expressions of type `Any` are present within your codebase.

--cobertura-xml-report DIR
:   Causes mypy to generate a Cobertura XML type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

--html-report / --xslt-html-report DIR
:   Causes mypy to generate an HTML type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

--linecount-report DIR
:   Causes mypy to generate a text file report documenting the functions
    and lines that are typed and untyped within your codebase.

--linecoverage-report DIR
:   Causes mypy to generate a JSON file that maps each source file’s
    absolute filename to a list of line numbers that belong to typed
    functions in that file.

--lineprecision-report DIR
:   Causes mypy to generate a flat text file report with per-module
    statistics of how many lines are typechecked etc.

--txt-report / --xslt-txt-report DIR
:   Causes mypy to generate a text file type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

--xml-report DIR
:   Causes mypy to generate an XML type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

## Enabling incomplete/experimental features

--enable-incomplete-feature {PreciseTupleTypes,InlineTypedDict,TypeForm}
:   Some features may require several mypy releases to implement, for example
    due to their complexity, potential for backwards incompatibility, or
    ambiguous semantics that would benefit from feedback from the community.
    You can enable such features for early preview using this flag. Note that
    it is not guaranteed that all features will be ultimately enabled by
    default. In *rare cases* we may decide to not go ahead with certain
    features.

List of currently incomplete/experimental features:

* `PreciseTupleTypes`: this feature will infer more precise tuple types in
  various scenarios. Before variadic types were added to the Python type system
  by [**PEP 646**](https://peps.python.org/pep-0646/), it was impossible to express a type like “a tuple with
  at least two integers”. The best type available was `tuple[int, ...]`.
  Therefore, mypy applied very lenient checking for variable-length tuples.
  Now this type can be expressed as `tuple[int, int, *tuple[int, ...]]`.
  For such more precise types (when explicitly *defined* by a user) mypy,
  for example, warns about unsafe index access, and generally handles them
  in a type-safe manner. However, to avoid problems in existing code, mypy
  does not *infer* these precise types when it technically can. Here are
  notable examples where `PreciseTupleTypes` infers more precise types:

  ```
  numbers: tuple[int, ...]

  more_numbers = (1, *numbers, 1)
  reveal_type(more_numbers)
  # Without PreciseTupleTypes: tuple[int, ...]
  # With PreciseTupleTypes: tuple[int, *tuple[int, ...], int]

  other_numbers = (1, 1) + numbers
  reveal_type(other_numbers)
  # Without PreciseTupleTypes: tuple[int, ...]
  # With PreciseTupleTypes: tuple[int, int, *tuple[int, ...]]

  if len(numbers) > 2:
      reveal_type(numbers)
      # Without PreciseTupleTypes: tuple[int, ...]
      # With PreciseTupleTypes: tuple[int, int, int, *tuple[int, ...]]
  else:
      reveal_type(numbers)
      # Without PreciseTupleTypes: tuple[int, ...]
      # With PreciseTupleTypes: tuple[()] | tuple[int] | tuple[int, int]
  ```
* `InlineTypedDict`: this feature enables non-standard syntax for inline
  [TypedDicts](typed_dict.html#typeddict), for example:

  ```
  def test_values() -> {"width": int, "description": str}:
      return {"width": 42, "description": "test"}
  ```
* `TypeForm`: this feature enables `TypeForm`, as described in
  PEP 747 – Annotating Type Forms <https://peps.python.org/pep-0747/>\_.

## Miscellaneous

--install-types
:   This flag causes mypy to install known missing stub packages for
    third-party libraries using pip. It will display the pip command
    that will be run, and expects a confirmation before installing
    anything. For security reasons, these stubs are limited to only a
    small subset of manually selected packages that have been
    verified by the typeshed team. These packages include only stub
    files and no executable code.

    If you use this option without providing any files or modules to
    type check, mypy will install stub packages suggested during the
    previous mypy run. If there are files or modules to type check,
    mypy first type checks those, and proposes to install missing
    stubs at the end of the run, but only if any missing modules were
    detected.

    Note

    This is new in mypy 0.900. Previous mypy versions included a
    selection of third-party package stubs, instead of having
    them installed separately.

--non-interactive
:   When used together with [`--install-types`](#cmdoption-mypy-install-types), this causes mypy to install all suggested stub
    packages using pip without asking for confirmation, and then
    continues to perform type checking using the installed stubs, if
    some files or modules are provided to type check.

    This is implemented as up to two mypy runs internally. The first run
    is used to find missing stub packages, and output is shown from
    this run only if no missing stub packages were found. If missing
    stub packages were found, they are installed and then another run
    is performed.

--junit-xml JUNIT\_XML\_OUTPUT\_FILE
:   Causes mypy to generate a JUnit XML test result document with
    type checking results. This can make it easier to integrate mypy
    with continuous integration (CI) tools.

--junit-format {global,per\_file}
:   If –junit-xml is set, specifies format.
    global (default): single test with all errors;
    per\_file: one test entry per file with failures.

--find-occurrences CLASS.MEMBER
:   This flag will make mypy print out all usages of a class member
    based on static type information. This feature is experimental.

--scripts-are-modules
:   This flag will give command line arguments that appear to be
    scripts (i.e. files whose name does not end in `.py`)
    a module name derived from the script name rather than the fixed
    name [`__main__`](https://docs.python.org/3/library/__main__.html#module-__main__ "(in Python v3.14)").

    This lets you check more than one script in a single mypy invocation.
    (The default [`__main__`](https://docs.python.org/3/library/__main__.html#module-__main__ "(in Python v3.14)") is technically more correct, but if you
    have many scripts that import a large package, the behavior enabled
    by this flag is often more convenient.)