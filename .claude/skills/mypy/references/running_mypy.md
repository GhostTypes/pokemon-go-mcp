# Running mypy and managing imports

The [Getting started](getting_started.html#getting-started) page should have already introduced you
to the basics of how to run mypy – pass in the files and directories
you want to type check via the command line:

```
$ mypy foo.py bar.py some_directory
```

This page discusses in more detail how exactly to specify what files
you want mypy to type check, how mypy discovers imported modules,
and recommendations on how to handle any issues you may encounter
along the way.

If you are interested in learning about how to configure the
actual way mypy type checks your code, see our
[The mypy command line](command_line.html#command-line) guide.

## Specifying code to be checked

Mypy lets you specify what files it should type check in several different ways.

1. First, you can pass in paths to Python files and directories you
   want to type check. For example:

   ```
   $ mypy file_1.py foo/file_2.py file_3.pyi some/directory
   ```

   The above command tells mypy it should type check all of the provided
   files together. In addition, mypy will recursively type check the
   entire contents of any provided directories.

   For more details about how exactly this is done, see
   [Mapping file paths to modules](#mapping-paths-to-modules).
2. Second, you can use the [`-m`](command_line.html#cmdoption-mypy-m) flag (long form: [`--module`](command_line.html#cmdoption-mypy-m)) to
   specify a module name to be type checked. The name of a module
   is identical to the name you would use to import that module
   within a Python program. For example, running:

   ```
   $ mypy -m html.parser
   ```

   …will type check the module `html.parser` (this happens to be
   a library stub).

   Mypy will use an algorithm very similar to the one Python uses to
   find where modules and imports are located on the file system.
   For more details, see [How imports are found](#finding-imports).
3. Third, you can use the [`-p`](command_line.html#cmdoption-mypy-p) (long form: [`--package`](command_line.html#cmdoption-mypy-p)) flag to
   specify a package to be (recursively) type checked. This flag
   is almost identical to the [`-m`](command_line.html#cmdoption-mypy-m) flag except that if you give it
   a package name, mypy will recursively type check all submodules
   and subpackages of that package. For example, running:

   ```
   $ mypy -p html
   ```

   …will type check the entire `html` package (of library stubs).
   In contrast, if we had used the [`-m`](command_line.html#cmdoption-mypy-m) flag, mypy would have type
   checked just `html`’s `__init__.py` file and anything imported
   from there.

   Note that we can specify multiple packages and modules on the
   command line. For example:

   ```
   $ mypy --package p.a --package p.b --module c
   ```
4. Fourth, you can also instruct mypy to directly type check small
   strings as programs by using the [`-c`](command_line.html#cmdoption-mypy-c) (long form: [`--command`](command_line.html#cmdoption-mypy-c))
   flag. For example:

   ```
   $ mypy -c 'x = [1, 2]; print(x())'
   ```

   …will type check the above string as a mini-program (and in this case,
   will report that `list[int]` is not callable).

You can also use the [`files`](config_file.html#confval-files) option in your `mypy.ini` file to specify which
files to check, in which case you can simply run `mypy` with no arguments.

## Reading a list of files from a file

Finally, any command-line argument starting with `@` reads additional
command-line arguments from the file following the `@` character.
This is primarily useful if you have a file containing a list of files
that you want to be type-checked: instead of using shell syntax like:

```
$ mypy $(cat file_of_files.txt)
```

you can use this instead:

```
$ mypy @file_of_files.txt
```

This file can technically also contain any command line flag, not
just file paths. However, if you want to configure many different
flags, the recommended approach is to use a
[configuration file](config_file.html#config-file) instead.

## Mapping file paths to modules

One of the main ways you can tell mypy what to type check
is by providing mypy a list of paths. For example:

```
$ mypy file_1.py foo/file_2.py file_3.pyi some/directory
```

This section describes how exactly mypy maps the provided paths
to modules to type check.

* Mypy will check all paths provided that correspond to files.
* Mypy will recursively discover and check all files ending in `.py` or
  `.pyi` in directory paths provided, after accounting for
  [`--exclude`](command_line.html#cmdoption-mypy-exclude).
* For each file to be checked, mypy will attempt to associate the file (e.g.
  `project/foo/bar/baz.py`) with a fully qualified module name (e.g.
  `foo.bar.baz`). The directory the package is in (`project`) is then
  added to mypy’s module search paths.

How mypy determines fully qualified module names depends on if the options
[`--no-namespace-packages`](command_line.html#cmdoption-mypy-no-namespace-packages) and
[`--explicit-package-bases`](command_line.html#cmdoption-mypy-explicit-package-bases) are set.

1. If [`--no-namespace-packages`](command_line.html#cmdoption-mypy-no-namespace-packages) is set,
   mypy will rely solely upon the presence of `__init__.py[i]` files to
   determine the fully qualified module name. That is, mypy will crawl up the
   directory tree for as long as it continues to find `__init__.py` (or
   `__init__.pyi`) files.

   For example, if your directory tree consists of `pkg/subpkg/mod.py`, mypy
   would require `pkg/__init__.py` and `pkg/subpkg/__init__.py` to exist in
   order correctly associate `mod.py` with `pkg.subpkg.mod`
2. The default case. If [`--namespace-packages`](command_line.html#cmdoption-mypy-no-namespace-packages) is on, but [`--explicit-package-bases`](command_line.html#cmdoption-mypy-explicit-package-bases) is off, mypy will allow for the possibility that
   directories without `__init__.py[i]` are packages. Specifically, mypy will
   look at all parent directories of the file and use the location of the
   highest `__init__.py[i]` in the directory tree to determine the top-level
   package.

   For example, say your directory tree consists solely of `pkg/__init__.py`
   and `pkg/a/b/c/d/mod.py`. When determining `mod.py`’s fully qualified
   module name, mypy will look at `pkg/__init__.py` and conclude that the
   associated module name is `pkg.a.b.c.d.mod`.
3. You’ll notice that the above case still relies on `__init__.py`. If
   you can’t put an `__init__.py` in your top-level package, but still wish to
   pass paths (as opposed to packages or modules using the `-p` or `-m`
   flags), [`--explicit-package-bases`](command_line.html#cmdoption-mypy-explicit-package-bases)
   provides a solution.

   With [`--explicit-package-bases`](command_line.html#cmdoption-mypy-explicit-package-bases), mypy
   will locate the nearest parent directory that is a member of the `MYPYPATH`
   environment variable, the [`mypy_path`](config_file.html#confval-mypy_path) config or is the current
   working directory. Mypy will then use the relative path to determine the
   fully qualified module name.

   For example, say your directory tree consists solely of
   `src/namespace_pkg/mod.py`. If you run the following command, mypy
   will correctly associate `mod.py` with `namespace_pkg.mod`:

   ```
   $ MYPYPATH=src mypy --namespace-packages --explicit-package-bases .
   ```

If you pass a file not ending in `.py[i]`, the module name assumed is
`__main__` (matching the behavior of the Python interpreter), unless
[`--scripts-are-modules`](command_line.html#cmdoption-mypy-scripts-are-modules) is passed.

Passing [`-v`](command_line.html#cmdoption-mypy-v) will show you the files and associated module
names that mypy will check.

## How mypy handles imports

When mypy encounters an `import` statement, it will first
[attempt to locate](#finding-imports) that module
or type stubs for that module in the file system. Mypy will then
type check the imported module. There are three different outcomes
of this process:

1. Mypy is unable to follow the import: the module either does not
   exist, or is a third party library that does not use type hints.
2. Mypy is able to follow and type check the import, but you did
   not want mypy to type check that module at all.
3. Mypy is able to successfully both follow and type check the
   module, and you want mypy to type check that module.

The third outcome is what mypy will do in the ideal case. The following
sections will discuss what to do in the other two cases.

## Missing imports

When you import a module, mypy may report that it is unable to follow
the import. This can cause errors that look like the following:

```
main.py:1: error: Skipping analyzing 'django': module is installed, but missing library stubs or py.typed marker
main.py:2: error: Library stubs not installed for "requests"
main.py:3: error: Cannot find implementation or library stub for module named "this_module_does_not_exist"
```

If you get any of these errors on an import, mypy will assume the type of that
module is `Any`, the dynamic type. This means attempting to access any
attribute of the module will automatically succeed:

```
# Error: Cannot find implementation or library stub for module named 'does_not_exist'
import does_not_exist

# But this type checks, and x will have type 'Any'
x = does_not_exist.foobar()
```

This can result in mypy failing to warn you about errors in your code. Since
operations on `Any` result in `Any`, these dynamic types can propagate
through your code, making type checking less effective. See
[Dynamically typed code](dynamic_typing.html#dynamic-typing) for more information.

The next sections describe what each of these errors means and recommended next steps; scroll to
the section that matches your error.

### Missing library stubs or py.typed marker

If you are getting a `Skipping analyzing X: module is installed, but missing library stubs or py.typed marker`,
error, this means mypy was able to find the module you were importing, but no
corresponding type hints.

Mypy will not try inferring the types of any 3rd party libraries you have installed
unless they either have declared themselves to be
[PEP 561 compliant stub package](installed_packages.html#installed-packages) (e.g. with a `py.typed` file) or have registered
themselves on [typeshed](https://github.com/python/typeshed), the repository
of types for the standard library and some 3rd party libraries.

If you are getting this error, try to obtain type hints for the library you’re using:

1. Upgrading the version of the library you’re using, in case a newer version
   has started to include type hints.
2. Searching to see if there is a [PEP 561 compliant stub package](installed_packages.html#installed-packages)
   corresponding to your third party library. Stub packages let you install
   type hints independently from the library itself.

   For example, if you want type hints for the `django` library, you can
   install the [django-stubs](https://pypi.org/project/django-stubs/) package.
3. [Writing your own stub files](stubs.html#stub-files) containing type hints for
   the library. You can point mypy at your type hints either by passing
   them in via the command line, by using the [`files`](config_file.html#confval-files) or [`mypy_path`](config_file.html#confval-mypy_path)
   config file options, or by
   adding the location to the `MYPYPATH` environment variable.

   These stub files do not need to be complete! A good strategy is to use
   [stubgen](stubgen.html#stubgen), a program that comes bundled with mypy, to generate a first
   rough draft of the stubs. You can then iterate on just the parts of the
   library you need.

   If you want to share your work, you can try contributing your stubs back
   to the library – see our documentation on creating
   [PEP 561 compliant packages](installed_packages.html#installed-packages).
4. Force mypy to analyze the library as best as it can (as if the library provided
   a `py.typed` file), despite it likely missing any type annotations. In general,
   the quality of type checking will be poor and mypy may have issues when
   analyzing code not designed to be type checked.

   You can do this via setting the
   [`--follow-untyped-imports`](command_line.html#cmdoption-mypy-follow-untyped-imports)
   command line flag or [`follow_untyped_imports`](config_file.html#confval-follow_untyped_imports) config file option to True.
   This option can be specified on a per-module basis as well:

   mypy.ini

   ```
   [mypy-untyped_package.*]
   follow_untyped_imports = True
   ```

   pyproject.toml

   ```
   [[tool.mypy.overrides]]
   module = ["untyped_package.*"]
   follow_untyped_imports = true
   ```

If you are unable to find any existing type hints nor have time to write your
own, you can instead *suppress* the errors.

All this will do is make mypy stop reporting an error on the line containing the
import: the imported module will continue to be of type `Any`, and mypy may
not catch errors in its use.

1. To suppress a *single* missing import error, add a `# type: ignore` at the end of the
   line containing the import.
2. To suppress *all* missing import errors from a single library, add
   a per-module section to your [mypy config file](config_file.html#config-file) setting
   [`ignore_missing_imports`](config_file.html#confval-ignore_missing_imports) to True for that library. For example,
   suppose your codebase
   makes heavy use of an (untyped) library named `foobar`. You can silence
   all import errors associated with that library and that library alone by
   adding the following section to your config file:

   mypy.ini

   ```
   [mypy-foobar.*]
   ignore_missing_imports = True
   ```

   pyproject.toml

   ```
   [[tool.mypy.overrides]]
   module = ["foobar.*"]
   ignore_missing_imports = true
   ```

   Note: this option is equivalent to adding a `# type: ignore` to every
   import of `foobar` in your codebase. For more information, see the
   documentation about configuring
   [import discovery](config_file.html#config-file-import-discovery) in config files.
   The `.*` after `foobar` will ignore imports of `foobar` modules
   and subpackages in addition to the `foobar` top-level package namespace.
3. To suppress *all* missing import errors for *all* untyped libraries
   in your codebase, use [`--disable-error-code=import-untyped`](command_line.html#cmdoption-mypy-ignore-missing-imports).
   See [Check that import target can be found [import-untyped]](error_code_list.html#code-import-untyped) for more details on this error code.

   You can also set [`disable_error_code`](config_file.html#confval-disable_error_code), like so:

   mypy.ini

   ```
   [mypy]
   disable_error_code = import-untyped
   ```

   pyproject.toml

   ```
   [tool.mypy]
   disable_error_code = ["import-untyped"]
   ```

   You can also set the [`--ignore-missing-imports`](command_line.html#cmdoption-mypy-ignore-missing-imports)
   command line flag or set the [`ignore_missing_imports`](config_file.html#confval-ignore_missing_imports) config file
   option to True in the *global* section of your mypy config file. We
   recommend avoiding `--ignore-missing-imports` if possible: it’s equivalent
   to adding a `# type: ignore` to all unresolved imports in your codebase.

### Library stubs not installed

If mypy can’t find stubs for a third-party library, and it knows that stubs exist for
the library, you will get a message like this:

```
main.py:1: error: Library stubs not installed for "yaml"
main.py:1: note: Hint: "python3 -m pip install types-PyYAML"
main.py:1: note: (or run "mypy --install-types" to install all missing stub packages)
```

You can resolve the issue by running the suggested pip commands.
If you’re running mypy in CI, you can ensure the presence of any stub packages
you need the same as you would any other test dependency, e.g. by adding them to
the appropriate `requirements.txt` file.

Alternatively, add the [`--install-types`](command_line.html#cmdoption-mypy-install-types)
to your mypy command to install all known missing stubs:

```
mypy --install-types
```

This is slower than explicitly installing stubs, since it effectively
runs mypy twice – the first time to find the missing stubs, and
the second time to type check your code properly after mypy has
installed the stubs. It also can make controlling stub versions harder,
resulting in less reproducible type checking.

By default, [`--install-types`](command_line.html#cmdoption-mypy-install-types) shows a confirmation prompt.
Use [`--non-interactive`](command_line.html#cmdoption-mypy-non-interactive) to install all suggested
stub packages without asking for confirmation *and* type check your code:

If you’ve already installed the relevant third-party libraries in an environment
other than the one mypy is running in, you can use [`--python-executable`](command_line.html#cmdoption-mypy-python-executable) flag to point to the Python executable for that
environment, and mypy will find packages installed for that Python executable.

If you’ve installed the relevant stub packages and are still getting this error,
see the [section below](#missing-type-hints-for-third-party-library).

### Cannot find implementation or library stub

If you are getting a `Cannot find implementation or library stub for module`
error, this means mypy was not able to find the module you are trying to
import, whether it comes bundled with type hints or not. If you are getting
this error, try:

1. Making sure your import does not contain a typo.
2. If the module is a third party library, making sure that mypy is able
   to find the interpreter containing the installed library.

   For example, if you are running your code in a virtualenv, make sure
   to install and use mypy within the virtualenv. Alternatively, if you
   want to use a globally installed mypy, set the
   [`--python-executable`](command_line.html#cmdoption-mypy-python-executable) command
   line flag to point the Python interpreter containing your installed
   third party packages.

   You can confirm that you are running mypy from the environment you expect
   by running it like `python -m mypy ...`. You can confirm that you are
   installing into the environment you expect by running pip like
   `python -m pip ...`.
3. Reading the [How imports are found](#finding-imports) section below to make sure you
   understand how exactly mypy searches for and finds modules and modify
   how you’re invoking mypy accordingly.
4. Directly specifying the directory containing the module you want to
   type check from the command line, by using the [`mypy_path`](config_file.html#confval-mypy_path)
   or [`files`](config_file.html#confval-files) config file options,
   or by using the `MYPYPATH` environment variable.

   Note: if the module you are trying to import is actually a *submodule* of
   some package, you should specify the directory containing the *entire* package.
   For example, suppose you are trying to add the module `foo.bar.baz`
   which is located at `~/foo-project/src/foo/bar/baz.py`. In this case,
   you must run `mypy ~/foo-project/src` (or set the `MYPYPATH` to
   `~/foo-project/src`).

## How imports are found

When mypy encounters an `import` statement or receives module
names from the command line via the [`--module`](command_line.html#cmdoption-mypy-m) or [`--package`](command_line.html#cmdoption-mypy-p)
flags, mypy tries to find the module on the file system similar
to the way Python finds it. However, there are some differences.

First, mypy has its own search path.
This is computed from the following items:

* The `MYPYPATH` environment variable
  (a list of directories, colon-separated on UNIX systems, semicolon-separated on Windows).
* The [`mypy_path`](config_file.html#confval-mypy_path) config file option.
* The directories containing the sources given on the command line
  (see [Mapping file paths to modules](#mapping-paths-to-modules)).
* The installed packages marked as safe for type checking (see
  [PEP 561 support](installed_packages.html#installed-packages))
* The relevant directories of the
  [typeshed](https://github.com/python/typeshed) repo.

Note

You cannot point to a stub-only package ([**PEP 561**](https://peps.python.org/pep-0561/)) via the `MYPYPATH`, it must be
installed (see [PEP 561 support](installed_packages.html#installed-packages))

Second, mypy searches for stub files in addition to regular Python files
and packages.
The rules for searching for a module `foo` are as follows:

* The search looks in each of the directories in the search path
  (see above) until a match is found.
* If a package named `foo` is found (i.e. a directory
  `foo` containing an `__init__.py` or `__init__.pyi` file)
  that’s a match.
* If a stub file named `foo.pyi` is found, that’s a match.
* If a Python module named `foo.py` is found, that’s a match.

These matches are tried in order, so that if multiple matches are found
in the same directory on the search path
(e.g. a package and a Python file, or a stub file and a Python file)
the first one in the above list wins.

In particular, if a Python file and a stub file are both present in the
same directory on the search path, only the stub file is used.
(However, if the files are in different directories, the one found
in the earlier directory is used.)

Setting [`mypy_path`](config_file.html#confval-mypy_path)/`MYPYPATH` is mostly useful in the case
where you want to try running mypy against multiple distinct
sets of files that happen to share some common dependencies.

For example, if you have multiple projects that happen to be
using the same set of work-in-progress stubs, it could be
convenient to just have your `MYPYPATH` point to a single
directory containing the stubs.

## Following imports

Mypy is designed to [doggedly follow all imports](#finding-imports),
even if the imported module is not a file you explicitly wanted mypy to check.

For example, suppose we have two modules `mycode.foo` and `mycode.bar`:
the former has type hints and the latter does not. We run
[`mypy -m mycode.foo`](command_line.html#cmdoption-mypy-m) and mypy discovers that `mycode.foo` imports
`mycode.bar`.

How do we want mypy to type check `mycode.bar`? Mypy’s behaviour here is
configurable – although we **strongly recommend** using the default –
by using the [`--follow-imports`](command_line.html#cmdoption-mypy-follow-imports) flag. This flag
accepts one of four string values:

* `normal` (the default, recommended) follows all imports normally and
  type checks all top level code (as well as the bodies of all
  functions and methods with at least one type annotation in
  the signature).
* `silent` behaves in the same way as `normal` but will
  additionally *suppress* any error messages.
* `skip` will *not* follow imports and instead will silently
  replace the module (and *anything imported from it*) with an
  object of type `Any`.
* `error` behaves in the same way as `skip` but is not quite as
  silent – it will flag the import as an error, like this:

  ```
  main.py:1: note: Import of "mycode.bar" ignored
  main.py:1: note: (Using --follow-imports=error, module not passed on command line)
  ```

If you are starting a new codebase and plan on using type hints from
the start, we **recommend** you use either [`--follow-imports=normal`](command_line.html#cmdoption-mypy-follow-imports)
(the default) or [`--follow-imports=error`](command_line.html#cmdoption-mypy-follow-imports). Either option will help
make sure you are not skipping checking any part of your codebase by
accident.

If you are planning on adding type hints to a large, existing code base,
we recommend you start by trying to make your entire codebase (including
files that do not use type hints) pass under [`--follow-imports=normal`](command_line.html#cmdoption-mypy-follow-imports).
This is usually not too difficult to do: mypy is designed to report as
few error messages as possible when it is looking at unannotated code.

Only if doing this is intractable, try passing mypy just the files
you want to type check and using [`--follow-imports=silent`](command_line.html#cmdoption-mypy-follow-imports).
Even if mypy is unable to perfectly type check a file, it can still glean some
useful information by parsing it (for example, understanding what methods
a given object has). See [Using mypy with an existing codebase](existing_code.html#existing-code) for more recommendations.

Adjusting import following behaviour is often most useful when restricted to
specific modules. This can be accomplished by setting a per-module
[`follow_imports`](config_file.html#confval-follow_imports) config option.

Warning

We do not recommend using `follow_imports=skip` unless you’re really sure
you know what you are doing. This option greatly restricts the analysis mypy
can perform and you will lose a lot of the benefits of type checking.

This is especially true at the global level. Setting a per-module
`follow_imports=skip` for a specific problematic module can be
useful without causing too much harm.

Note

If you’re looking to resolve import errors related to libraries, try following
the advice in [Missing imports](#fix-missing-imports) before messing with `follow_imports`.