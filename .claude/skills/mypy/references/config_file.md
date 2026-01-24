# The mypy configuration file

Mypy is very configurable. This is most useful when introducing typing to
an existing codebase. See [Using mypy with an existing codebase](existing_code.html#existing-code) for concrete advice for
that situation.

Mypy supports reading configuration settings from a file. By default, mypy will
discover configuration files by walking up the file system (up until the root of
a repository or the root of the filesystem). In each directory, it will look for
the following configuration files (in this order):

> 1. `mypy.ini`
> 2. `.mypy.ini`
> 3. `pyproject.toml` (containing a `[tool.mypy]` section)
> 4. `setup.cfg` (containing a `[mypy]` section)

If no configuration file is found by this method, mypy will then look for
configuration files in the following locations (in this order):

> 1. `$XDG_CONFIG_HOME/mypy/config`
> 2. `~/.config/mypy/config`
> 3. `~/.mypy.ini`

The [`--config-file`](command_line.html#cmdoption-mypy-config-file) command-line flag has the
highest precedence and must point towards a valid configuration file;
otherwise mypy will report an error and exit. Without the command line option,
mypy will look for configuration files in the precedence order above.

It is important to understand that there is no merging of configuration
files, as it would lead to ambiguity.

Most flags correspond closely to [command-line flags](command_line.html#command-line) but there are some differences in flag names and some
flags may take a different value based on the module being processed.

Some flags support user home directory and environment variable expansion.
To refer to the user home directory, use `~` at the beginning of the path.
To expand environment variables use `$VARNAME` or `${VARNAME}`.

## Config file format

The configuration file format is the usual
[ini file](https://docs.python.org/3/library/configparser.html "(in Python v3.14)") format. It should contain
section names in square brackets and flag settings of the form
NAME = VALUE. Comments start with `#` characters.

* A section named `[mypy]` must be present. This specifies
  the global flags.
* Additional sections named `[mypy-PATTERN1,PATTERN2,...]` may be
  present, where `PATTERN1`, `PATTERN2`, etc., are comma-separated
  patterns of fully-qualified module names, with some components optionally
  replaced by the ‘\*’ character (e.g. `foo.bar`, `foo.bar.*`, `foo.*.baz`).
  These sections specify additional flags that only apply to *modules*
  whose name matches at least one of the patterns.

  A pattern of the form `qualified_module_name` matches only the named module,
  while `dotted_module_name.*` matches `dotted_module_name` and any
  submodules (so `foo.bar.*` would match all of `foo.bar`,
  `foo.bar.baz`, and `foo.bar.baz.quux`).

  Patterns may also be “unstructured” wildcards, in which stars may
  appear in the middle of a name (e.g
  `site.*.migrations.*`). Stars match zero or more module
  components (so `site.*.migrations.*` can match `site.migrations`).

  When options conflict, the precedence order for configuration is:

  > 1. [Inline configuration](inline_config.html#inline-config) in the source file
  > 2. Sections with concrete module names (`foo.bar`)
  > 3. Sections with “unstructured” wildcard patterns (`foo.*.baz`),
  >    with sections later in the configuration file overriding
  >    sections earlier.
  > 4. Sections with “well-structured” wildcard patterns
  >    (`foo.bar.*`), with more specific overriding more general.
  > 5. Command line options.
  > 6. Top-level configuration file options.

The difference in precedence order between “structured” patterns (by
specificity) and “unstructured” patterns (by order in the file) is
unfortunate, and is subject to change in future versions.

Note

The [`warn_unused_configs`](#confval-warn_unused_configs) flag may be useful to debug misspelled
section names.

Note

Configuration flags are liable to change between releases.

## Per-module and global options

Some of the config options may be set either globally (in the `[mypy]` section)
or on a per-module basis (in sections like `[mypy-foo.bar]`).

If you set an option both globally and for a specific module, the module configuration
options take precedence. This lets you set global defaults and override them on a
module-by-module basis. If multiple pattern sections match a module, [the options from the
most specific section are used where they disagree](#config-precedence).

Some other options, as specified in their description,
may only be set in the global section (`[mypy]`).

## Inverting option values

Options that take a boolean value may be inverted by adding `no_` to
their name or by (when applicable) swapping their prefix from
`disallow` to `allow` (and vice versa).

## Example `mypy.ini`

Here is an example of a `mypy.ini` file. To use this config file, place it at the root
of your repo and run mypy.

```
# Global options:

[mypy]
warn_return_any = True
warn_unused_configs = True

# Per-module options:

[mypy-mycode.foo.*]
disallow_untyped_defs = True

[mypy-mycode.bar]
warn_return_any = False

[mypy-somelibrary]
ignore_missing_imports = True
```

This config file specifies two global options in the `[mypy]` section. These two
options will:

1. Report an error whenever a function returns a value that is inferred
   to have type `Any`.
2. Report any config options that are unused by mypy. (This will help us catch typos
   when making changes to our config file).

Next, this module specifies three per-module options. The first two options change how mypy
type checks code in `mycode.foo.*` and `mycode.bar`, which we assume here are two modules
that you wrote. The final config option changes how mypy type checks `somelibrary`, which we
assume here is some 3rd party library you’ve installed and are importing. These options will:

1. Selectively disallow untyped function definitions only within the `mycode.foo`
   package – that is, only for function definitions defined in the
   `mycode/foo` directory.
2. Selectively *disable* the “function is returning any” warnings within
   `mycode.bar` only. This overrides the global default we set earlier.
3. Suppress any error messages generated when your codebase tries importing the
   module `somelibrary`. This is useful if `somelibrary` is some 3rd party library
   missing type hints.

## Import discovery

For more information, see the [Import discovery](command_line.html#import-discovery)
section of the command line docs.

mypy\_path
:   Type:
    :   string

    Specifies the paths to use, after trying the paths from `MYPYPATH` environment
    variable. Useful if you’d like to keep stubs in your repo, along with the config file.
    Multiple paths are always separated with a `:` or `,` regardless of the platform.
    User home directory and environment variables will be expanded.

    Relative paths are treated relative to the working directory of the mypy command,
    not the config file.
    Use the `MYPY_CONFIG_FILE_DIR` environment variable to refer to paths relative to
    the config file (e.g. `mypy_path = $MYPY_CONFIG_FILE_DIR/src`).

    This option may only be set in the global section (`[mypy]`).

    **Note:** On Windows, use UNC paths to avoid using `:` (e.g. `\\127.0.0.1\X$\MyDir` where `X` is the drive letter).

files
:   Type:
    :   comma-separated list of strings

    A comma-separated list of paths which should be checked by mypy if none are given on the command
    line. Supports recursive file globbing using [`glob`](https://docs.python.org/3/library/glob.html#module-glob "(in Python v3.14)"), where `*` (e.g. `*.py`) matches
    files in the current directory and `**/` (e.g. `**/*.py`) matches files in any directories below
    the current one. User home directory and environment variables will be expanded.

    This option may only be set in the global section (`[mypy]`).

modules
:   Type:
    :   comma-separated list of strings

    A comma-separated list of packages which should be checked by mypy if none are given on the command
    line. Mypy *will not* recursively type check any submodules of the provided
    module.

    This option may only be set in the global section (`[mypy]`).

packages
:   Type:
    :   comma-separated list of strings

    A comma-separated list of packages which should be checked by mypy if none are given on the command
    line. Mypy *will* recursively type check any submodules of the provided
    package. This flag is identical to [`modules`](#confval-modules) apart from this
    behavior.

    This option may only be set in the global section (`[mypy]`).

exclude
:   Type:
    :   regular expression

    A regular expression that matches file names, directory names and paths
    which mypy should ignore while recursively discovering files to check.
    Use forward slashes (`/`) as directory separators on all platforms.

    ```
    [mypy]
    exclude = (?x)(
        ^one\.py$    # files named "one.py"
        | two\.pyi$  # or files ending with "two.pyi"
        | ^three\.   # or files starting with "three."
      )
    ```

    Crafting a single regular expression that excludes multiple files while remaining
    human-readable can be a challenge. The above example demonstrates one approach.
    `(?x)` enables the `VERBOSE` flag for the subsequent regular expression, which
    [`ignores most whitespace and supports comments`](https://docs.python.org/3/library/re.html#re.VERBOSE "(in Python v3.14)").
    The above is equivalent to: `(^one\.py$|two\.pyi$|^three\.)`.

    For more details, see [`--exclude`](command_line.html#cmdoption-mypy-exclude).

    This option may only be set in the global section (`[mypy]`).

    Note

    Note that the TOML equivalent differs slightly. It can be either a single string
    (including a multi-line string) – which is treated as a single regular
    expression – or an array of such strings. The following TOML examples are
    equivalent to the above INI example.

    Array of strings:

    ```
    [tool.mypy]
    exclude = [
        "^one\\.py$",  # TOML's double-quoted strings require escaping backslashes
        'two\.pyi$',  # but TOML's single-quoted strings do not
        '^three\.',
    ]
    ```

    A single, multi-line string:

    ```
    [tool.mypy]
    exclude = '''(?x)(
        ^one\.py$    # files named "one.py"
        | two\.pyi$  # or files ending with "two.pyi"
        | ^three\.   # or files starting with "three."
    )'''  # TOML's single-quoted strings do not require escaping backslashes
    ```

    See [Using a pyproject.toml file](#using-a-pyproject-toml).

exclude\_gitignore
:   Type:
    :   boolean

    Default:
    :   False

    This flag will add everything that matches `.gitignore` file(s) to [`exclude`](#confval-exclude).
    This option may only be set in the global section (`[mypy]`).

namespace\_packages
:   Type:
    :   boolean

    Default:
    :   True

    Enables [**PEP 420**](https://peps.python.org/pep-0420/) style namespace packages. See the
    corresponding flag [`--no-namespace-packages`](command_line.html#cmdoption-mypy-no-namespace-packages)
    for more information.

    This option may only be set in the global section (`[mypy]`).

explicit\_package\_bases
:   Type:
    :   boolean

    Default:
    :   False

    This flag tells mypy that top-level packages will be based in either the
    current directory, or a member of the `MYPYPATH` environment variable or
    [`mypy_path`](#confval-mypy_path) config option. This option is only useful in
    the absence of \_\_init\_\_.py. See [Mapping file
    paths to modules](running_mypy.html#mapping-paths-to-modules) for details.

    This option may only be set in the global section (`[mypy]`).

ignore\_missing\_imports
:   Type:
    :   boolean

    Default:
    :   False

    Suppresses error messages about imports that cannot be resolved.

    If this option is used in a per-module section, the module name should
    match the name of the *imported* module, not the module containing the
    import statement.

follow\_untyped\_imports
:   Type:
    :   boolean

    Default:
    :   False

    Makes mypy analyze imports from installed packages even if missing a
    [py.typed marker or stubs](installed_packages.html#installed-packages).

    If this option is used in a per-module section, the module name should
    match the name of the *imported* module, not the module containing the
    import statement.

    Warning

    Note that analyzing all unannotated modules might result in issues
    when analyzing code not designed to be type checked and may significantly
    increase how long mypy takes to run.

follow\_imports
:   Type:
    :   string

    Default:
    :   `normal`

    Directs what to do with imports when the imported module is found
    as a `.py` file and not part of the files, modules and packages
    provided on the command line.

    The four possible values are `normal`, `silent`, `skip` and
    `error`. For explanations see the discussion for the
    [`--follow-imports`](command_line.html#cmdoption-mypy-follow-imports) command line flag.

    Using this option in a per-module section (potentially with a wildcard,
    as described at the top of this page) is a good way to prevent mypy from
    checking portions of your code.

    If this option is used in a per-module section, the module name should
    match the name of the *imported* module, not the module containing the
    import statement.

follow\_imports\_for\_stubs
:   Type:
    :   boolean

    Default:
    :   False

    Determines whether to respect the [`follow_imports`](#confval-follow_imports) setting even for
    stub (`.pyi`) files.

    Used in conjunction with [`follow_imports=skip`](#confval-follow_imports), this can be used
    to suppress the import of a module from `typeshed`, replacing it
    with `Any`.

    Used in conjunction with [`follow_imports=error`](#confval-follow_imports), this can be used
    to make any use of a particular `typeshed` module an error.

    Note

    This is not supported by the mypy daemon.

python\_executable
:   Type:
    :   string

    Specifies the path to the Python executable to inspect to collect
    a list of available [PEP 561 packages](installed_packages.html#installed-packages). User
    home directory and environment variables will be expanded. Defaults to
    the executable used to run mypy.

    This option may only be set in the global section (`[mypy]`).

no\_site\_packages
:   Type:
    :   boolean

    Default:
    :   False

    Disables using type information in installed packages (see [**PEP 561**](https://peps.python.org/pep-0561/)).
    This will also disable searching for a usable Python executable. This acts
    the same as [`--no-site-packages`](command_line.html#cmdoption-mypy-no-site-packages) command
    line flag.

no\_silence\_site\_packages
:   Type:
    :   boolean

    Default:
    :   False

    Enables reporting error messages generated within installed packages (see
    [**PEP 561**](https://peps.python.org/pep-0561/) for more details on distributing type information). Those error
    messages are suppressed by default, since you are usually not able to
    control errors in 3rd party code.

    This option may only be set in the global section (`[mypy]`).

## Platform configuration

python\_version
:   Type:
    :   string

    Specifies the Python version used to parse and check the target
    program. The string should be in the format `MAJOR.MINOR` –
    for example `3.9`. The default is the version of the Python
    interpreter used to run mypy.

    This option may only be set in the global section (`[mypy]`).

platform
:   Type:
    :   string

    Specifies the OS platform for the target program, for example
    `darwin` or `win32` (meaning OS X or Windows, respectively).
    The default is the current platform as revealed by Python’s
    [`sys.platform`](https://docs.python.org/3/library/sys.html#sys.platform "(in Python v3.14)") variable.

    This option may only be set in the global section (`[mypy]`).

always\_true
:   Type:
    :   comma-separated list of strings

    Specifies a list of variables that mypy will treat as
    compile-time constants that are always true.

always\_false
:   Type:
    :   comma-separated list of strings

    Specifies a list of variables that mypy will treat as
    compile-time constants that are always false.

## Disallow dynamic typing

For more information, see the [Disallow dynamic typing](command_line.html#disallow-dynamic-typing)
section of the command line docs.

disallow\_any\_unimported
:   Type:
    :   boolean

    Default:
    :   False

    Disallows usage of types that come from unfollowed imports (anything imported from
    an unfollowed import is automatically given a type of `Any`).

disallow\_any\_expr
:   Type:
    :   boolean

    Default:
    :   False

    Disallows all expressions in the module that have type `Any`.

disallow\_any\_decorated
:   Type:
    :   boolean

    Default:
    :   False

    Disallows functions that have `Any` in their signature after decorator transformation.

disallow\_any\_explicit
:   Type:
    :   boolean

    Default:
    :   False

    Disallows explicit `Any` in type positions such as type annotations and generic
    type parameters.

disallow\_any\_generics
:   Type:
    :   boolean

    Default:
    :   False

    Disallows usage of generic types that do not specify explicit type parameters.

disallow\_subclassing\_any
:   Type:
    :   boolean

    Default:
    :   False

    Disallows subclassing a value of type `Any`.

## Untyped definitions and calls

For more information, see the [Untyped definitions and calls](command_line.html#untyped-definitions-and-calls)
section of the command line docs.

disallow\_untyped\_calls
:   Type:
    :   boolean

    Default:
    :   False

    Disallows calling functions without type annotations from functions with type
    annotations. Note that when used in per-module options, it enables/disables
    this check **inside** the module(s) specified, not for functions that come
    from that module(s), for example config like this:

    ```
    [mypy]
    disallow_untyped_calls = True

    [mypy-some.library.*]
    disallow_untyped_calls = False
    ```

    will disable this check inside `some.library`, not for your code that
    imports `some.library`. If you want to selectively disable this check for
    all your code that imports `some.library` you should instead use
    [`untyped_calls_exclude`](#confval-untyped_calls_exclude), for example:

    ```
    [mypy]
    disallow_untyped_calls = True
    untyped_calls_exclude = some.library
    ```

untyped\_calls\_exclude
:   Type:
    :   comma-separated list of strings

    Selectively excludes functions and methods defined in specific packages,
    modules, and classes from action of [`disallow_untyped_calls`](#confval-disallow_untyped_calls).
    This also applies to all submodules of packages (i.e. everything inside
    a given prefix). Note, this option does not support per-file configuration,
    the exclusions list is defined globally for all your code.

disallow\_untyped\_defs
:   Type:
    :   boolean

    Default:
    :   False

    Disallows defining functions without type annotations or with incomplete type
    annotations (a superset of [`disallow_incomplete_defs`](#confval-disallow_incomplete_defs)).

    For example, it would report an error for `def f(a, b)` and `def f(a: int, b)`.

disallow\_incomplete\_defs
:   Type:
    :   boolean

    Default:
    :   False

    Disallows defining functions with incomplete type annotations, while still
    allowing entirely unannotated definitions.

    For example, it would report an error for `def f(a: int, b)` but not `def f(a, b)`.

check\_untyped\_defs
:   Type:
    :   boolean

    Default:
    :   False

    Type-checks the interior of functions without type annotations.

disallow\_untyped\_decorators
:   Type:
    :   boolean

    Default:
    :   False

    Reports an error whenever a function with type annotations is decorated with a
    decorator without annotations.

## None and Optional handling

For more information, see the [None and Optional handling](command_line.html#none-and-optional-handling)
section of the command line docs.

implicit\_optional
:   Type:
    :   boolean

    Default:
    :   False

    Causes mypy to treat parameters with a `None`
    default value as having an implicit optional type (`T | None`).

    **Note:** This was True by default in mypy versions 0.980 and earlier.

strict\_optional
:   Type:
    :   boolean

    Default:
    :   True

    Effectively disables checking of optional
    types and `None` values. With this option, mypy doesn’t
    generally check the use of `None` values – it is treated
    as compatible with every type.

    Warning

    `strict_optional = false` is evil. Avoid using it and definitely do
    not use it without understanding what it does.

## Configuring warnings

For more information, see the [Configuring warnings](command_line.html#configuring-warnings)
section of the command line docs.

warn\_redundant\_casts
:   Type:
    :   boolean

    Default:
    :   False

    Warns about casting an expression to its inferred type.

    This option may only be set in the global section (`[mypy]`).

warn\_unused\_ignores
:   Type:
    :   boolean

    Default:
    :   False

    Warns about unneeded `# type: ignore` comments.

warn\_no\_return
:   Type:
    :   boolean

    Default:
    :   True

    Shows errors for missing return statements on some execution paths.

warn\_return\_any
:   Type:
    :   boolean

    Default:
    :   False

    Shows a warning when returning a value with type `Any` from a function
    declared with a non- `Any` return type.

warn\_unreachable
:   Type:
    :   boolean

    Default:
    :   False

    Shows a warning when encountering any code inferred to be unreachable or
    redundant after performing type analysis.

deprecated\_calls\_exclude
:   Type:
    :   comma-separated list of strings

    Selectively excludes functions and methods defined in specific packages,
    modules, and classes from the [deprecated](error_code_list2.html#code-deprecated) error code.
    This also applies to all submodules of packages (i.e. everything inside
    a given prefix). Note, this option does not support per-file configuration,
    the exclusions list is defined globally for all your code.

## Suppressing errors

Note: these configuration options are available in the config file only. There is
no analog available via the command line options.

ignore\_errors
:   Type:
    :   boolean

    Default:
    :   False

    Ignores all non-fatal errors.

## Miscellaneous strictness flags

For more information, see the [Miscellaneous strictness flags](command_line.html#miscellaneous-strictness-flags)
section of the command line docs.

allow\_untyped\_globals
:   Type:
    :   boolean

    Default:
    :   False

    Causes mypy to suppress errors caused by not being able to fully
    infer the types of global and class variables.

allow\_redefinition\_new
:   Type:
    :   boolean

    Default:
    :   False

    By default, mypy won’t allow a variable to be redefined with an
    unrelated type. This *experimental* flag enables the redefinition of
    unannotated variables with an arbitrary type. You will also need to enable
    [`local_partial_types`](#confval-local_partial_types).
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
    release, along with [`local_partial_types`](#confval-local_partial_types).

allow\_redefinition
:   Type:
    :   boolean

    Default:
    :   False

    Allows variables to be redefined with an arbitrary type, as long as the redefinition
    is in the same block and nesting level as the original definition.
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

local\_partial\_types
:   Type:
    :   boolean

    Default:
    :   False

    Disallows inferring variable type for `None` from two assignments in different scopes.
    This is always implicitly enabled when using the [mypy daemon](mypy_daemon.html#mypy-daemon).
    This will be enabled by default in a future mypy release.

disable\_error\_code
:   Type:
    :   comma-separated list of strings

    Allows disabling one or multiple error codes globally.

enable\_error\_code
:   Type:
    :   comma-separated list of strings

    Allows enabling one or multiple error codes globally.

    Note: This option will override disabled error codes from the disable\_error\_code option.

extra\_checks
:   Type:
    :   boolean

    Default:
    :   False

    This flag enables additional checks that are technically correct but may be impractical.
    See [`mypy --extra-checks`](command_line.html#cmdoption-mypy-extra-checks) for more info.

implicit\_reexport
:   Type:
    :   boolean

    Default:
    :   True

    By default, imported values to a module are treated as exported and mypy allows
    other modules to import them. When false, mypy will not re-export unless
    the item is imported using from-as or is included in `__all__`. Note that mypy
    treats stub files as if this is always disabled. For example:

    ```
    # This won't re-export the value
    from foo import bar
    # This will re-export it as bar and allow other modules to import it
    from foo import bar as bar
    # This will also re-export bar
    from foo import bar
    __all__ = ['bar']
    ```

strict\_equality
:   Type:
    :   boolean

    Default:
    :   False

    Prohibit equality checks, identity checks, and container checks between
    non-overlapping types (except `None`).

strict\_equality\_for\_none
:   Type:
    :   boolean

    Default:
    :   False

    Include `None` in strict equality checks (requires [`strict_equality`](#confval-strict_equality)
    to be activated).

strict\_bytes
:   Type:
    :   boolean

    Default:
    :   False

    Disable treating `bytearray` and `memoryview` as subtypes of `bytes`.
    This will be enabled by default in *mypy 2.0*.

strict
:   Type:
    :   boolean

    Default:
    :   False

    Enable all optional error checking flags. You can see the list of
    flags enabled by strict mode in the full [`mypy --help`](command_line.html#cmdoption-mypy-h)
    output.

    Note: the exact list of flags enabled by [`strict`](#confval-strict) may
    change over time.

## Configuring error messages

For more information, see the [Configuring error messages](command_line.html#configuring-error-messages)
section of the command line docs.

These options may only be set in the global section (`[mypy]`).

show\_error\_context
:   Type:
    :   boolean

    Default:
    :   False

    Prefixes each error with the relevant context.

show\_column\_numbers
:   Type:
    :   boolean

    Default:
    :   False

    Shows column numbers in error messages.

show\_error\_code\_links
:   Type:
    :   boolean

    Default:
    :   False

    Shows documentation link to corresponding error code.

hide\_error\_codes
:   Type:
    :   boolean

    Default:
    :   False

    Hides error codes in error messages. See [Error codes](error_codes.html#error-codes) for more information.

pretty
:   Type:
    :   boolean

    Default:
    :   False

    Use visually nicer output in error messages: use soft word wrap,
    show source code snippets, and show error location markers.

color\_output
:   Type:
    :   boolean

    Default:
    :   True

    Shows error messages with color enabled.

error\_summary
:   Type:
    :   boolean

    Default:
    :   True

    Shows a short summary line after error messages.

show\_absolute\_path
:   Type:
    :   boolean

    Default:
    :   False

    Show absolute paths to files.

force\_union\_syntax
:   Type:
    :   boolean

    Default:
    :   False

    Always use `Union[]` and `Optional[]` for union types
    in error messages (instead of the `|` operator),
    even on Python 3.10+.

## Incremental mode

These options may only be set in the global section (`[mypy]`).

incremental
:   Type:
    :   boolean

    Default:
    :   True

    Enables [incremental mode](command_line.html#incremental).

cache\_dir
:   Type:
    :   string

    Default:
    :   `.mypy_cache`

    Specifies the location where mypy stores incremental cache info.
    User home directory and environment variables will be expanded.
    This setting will be overridden by the `MYPY_CACHE_DIR` environment
    variable.

    Note that the cache is only read when incremental mode is enabled
    but is always written to, unless the value is set to `/dev/null`
    (UNIX) or `nul` (Windows).

sqlite\_cache
:   Type:
    :   boolean

    Default:
    :   False

    Use an [SQLite](https://www.sqlite.org/) database to store the cache.

cache\_fine\_grained
:   Type:
    :   boolean

    Default:
    :   False

    Include fine-grained dependency information in the cache for the mypy daemon.

skip\_version\_check
:   Type:
    :   boolean

    Default:
    :   False

    Makes mypy use incremental cache data even if it was generated by a
    different version of mypy. (By default, mypy will perform a version
    check and regenerate the cache if it was written by older versions of mypy.)

skip\_cache\_mtime\_checks
:   Type:
    :   boolean

    Default:
    :   False

    Skip cache internal consistency checks based on mtime.

## Advanced options

These options may only be set in the global section (`[mypy]`).

plugins
:   Type:
    :   comma-separated list of strings

    A comma-separated list of mypy plugins. See [Extending mypy using plugins](extending_mypy.html#extending-mypy-using-plugins).

pdb
:   Type:
    :   boolean

    Default:
    :   False

    Invokes [`pdb`](https://docs.python.org/3/library/pdb.html#module-pdb "(in Python v3.14)") on fatal error.

show\_traceback
:   Type:
    :   boolean

    Default:
    :   False

    Shows traceback on fatal error.

raise\_exceptions
:   Type:
    :   boolean

    Default:
    :   False

    Raise exception on fatal error.

custom\_typing\_module
:   Type:
    :   string

    Specifies a custom module to use as a substitute for the [`typing`](https://docs.python.org/3/library/typing.html#module-typing "(in Python v3.14)") module.

custom\_typeshed\_dir
:   Type:
    :   string

    This specifies the directory where mypy looks for standard library typeshed
    stubs, instead of the typeshed that ships with mypy. This is
    primarily intended to make it easier to test typeshed changes before
    submitting them upstream, but also allows you to use a forked version of
    typeshed.

    User home directory and environment variables will be expanded.

    Note that this doesn’t affect third-party library stubs. To test third-party stubs,
    for example try `MYPYPATH=stubs/six mypy ...`.

warn\_incomplete\_stub
:   Type:
    :   boolean

    Default:
    :   False

    Warns about missing type annotations in typeshed. This is only relevant
    in combination with [`disallow_untyped_defs`](#confval-disallow_untyped_defs) or [`disallow_incomplete_defs`](#confval-disallow_incomplete_defs).

## Report generation

If these options are set, mypy will generate a report in the specified
format into the specified directory.

Warning

Generating reports disables incremental mode and can significantly slow down
your workflow. It is recommended to enable reporting only for specific runs
(e.g. in CI).

any\_exprs\_report
:   Type:
    :   string

    Causes mypy to generate a text file report documenting how many
    expressions of type `Any` are present within your codebase.

cobertura\_xml\_report
:   Type:
    :   string

    Causes mypy to generate a Cobertura XML type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

html\_report / xslt\_html\_report
:   Type:
    :   string

    Causes mypy to generate an HTML type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

linecount\_report
:   Type:
    :   string

    Causes mypy to generate a text file report documenting the functions
    and lines that are typed and untyped within your codebase.

linecoverage\_report
:   Type:
    :   string

    Causes mypy to generate a JSON file that maps each source file’s
    absolute filename to a list of line numbers that belong to typed
    functions in that file.

lineprecision\_report
:   Type:
    :   string

    Causes mypy to generate a flat text file report with per-module
    statistics of how many lines are typechecked etc.

txt\_report / xslt\_txt\_report
:   Type:
    :   string

    Causes mypy to generate a text file type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

xml\_report
:   Type:
    :   string

    Causes mypy to generate an XML type checking coverage report.

    To generate this report, you must either manually install the [lxml](https://pypi.org/project/lxml/)
    library or specify mypy installation with the setuptools extra
    `mypy[reports]`.

## Miscellaneous

These options may only be set in the global section (`[mypy]`).

junit\_xml
:   Type:
    :   string

    Causes mypy to generate a JUnit XML test result document with
    type checking results. This can make it easier to integrate mypy
    with continuous integration (CI) tools.

junit\_format
:   Type:
    :   string

    Default:
    :   `global`

    If junit\_xml is set, specifies format.
    global (default): single test with all errors;
    per\_file: one test entry per file with failures.

scripts\_are\_modules
:   Type:
    :   boolean

    Default:
    :   False

    Makes script `x` become module `x` instead of `__main__`. This is
    useful when checking multiple scripts in a single run.

warn\_unused\_configs
:   Type:
    :   boolean

    Default:
    :   False

    Warns about per-module sections in the config file that do not
    match any files processed when invoking mypy.
    (This requires turning off incremental mode using [`incremental = False`](#confval-incremental).)

verbosity
:   Type:
    :   integer

    Default:
    :   0

    Controls how much debug output will be generated. Higher numbers are more verbose.

## Using a pyproject.toml file

Instead of using a `mypy.ini` file, a `pyproject.toml` file (as specified by
[PEP 518](https://www.python.org/dev/peps/pep-0518/)) may be used instead. A few notes on doing so:

* The `[mypy]` section should have `tool.` prepended to its name:

  + I.e., `[mypy]` would become `[tool.mypy]`
* The module specific sections should be moved into `[[tool.mypy.overrides]]` sections:

  + For example, `[mypy-packagename]` would become:

```
[[tool.mypy.overrides]]
module = 'packagename'
...
```

* Multi-module specific sections can be moved into a single `[[tool.mypy.overrides]]` section with a
  module property set to an array of modules:

  + For example, `[mypy-packagename,packagename2]` would become:

```
[[tool.mypy.overrides]]
module = [
    'packagename',
    'packagename2'
]
...
```

* The following care should be given to values in the `pyproject.toml` files as compared to `ini` files:

  + Strings must be wrapped in double quotes, or single quotes if the string contains special characters
  + Boolean values should be all lower case

Please see the [TOML Documentation](https://toml.io/) for more details and information on
what is allowed in a `toml` file. See [PEP 518](https://www.python.org/dev/peps/pep-0518/) for more information on the layout
and structure of the `pyproject.toml` file.

## Example `pyproject.toml`

Here is an example of a `pyproject.toml` file. To use this config file, place it at the root
of your repo (or append it to the end of an existing `pyproject.toml` file) and run mypy.

```
# mypy global options:

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
exclude = [
    '^file1\.py$',  # TOML literal string (single-quotes, no escaping necessary)
    "^file2\\.py$",  # TOML basic string (double-quotes, backslash and other characters need escaping)
]

# mypy per-module options:

[[tool.mypy.overrides]]
module = "mycode.foo.*"
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "mycode.bar"
warn_return_any = false

[[tool.mypy.overrides]]
module = [
    "somelibrary",
    "some_other_library"
]
ignore_missing_imports = true
```