# HyperLang Built-in Functions

Built-ins use command syntax. Unless stated otherwise, the destination variable
must already exist and have the matching HyperLang type.

## Character and string functions

```hl
ascii <value_or_variable> <string_destination>
chr <integer_or_variable> <string_destination>
ord <character_or_variable> <integer_destination>
format <value_or_variable> <format_spec> <string_destination>
repr <value_or_variable> <string_destination>
```

`format` also accepts `format <value_or_variable> <string_destination>` to use
the default format specification. For example:

```hl
define var code: int = 9731
define var symbol: string = ""
chr code symbol
text output symbol
```

## Iteration and collections

These functions return a list, except `slice`, which preserves the source
sequence type. Their destination variables should be declared as `list` (or as
the source type for `slice`).

```hl
enumerate <iterable> <list_destination> [start]
filter <function> <iterable> <list_destination>
iter <iterable> <iterator_destination>
map <function> <iterable> <list_destination>
next <iterator> <destination> [default]
range <stop> <list_destination>
range <start> <stop> <list_destination> [step]
reversed <iterable> <list_destination>
slice <sequence> <start> <stop> <destination> [step]
sorted <iterable> <list_destination> [reverse]
zip <iterable1> <iterable2> [...] <list_destination>
```

`iter` creates its destination variable if it does not already exist. `next`
raises an error when the iterator is exhausted and no default is supplied.
`enumerate` produces `(index, value)` tuples; `zip` produces tuples. `sorted`
accepts `true` or `false` for its optional `reverse` argument.

`map` and `filter` accept a built-in unary function name (such as `abs`, `int`,
`float`, `str`, `bool`, `ascii`, `repr`, or `len`) or a user-defined function
that takes one parameter and returns a value. Functions can be declared with
parameters, called with arguments, and return a value:

```hl
func define is_positive value
    define var result: bool = false
    compare value > 0 result
    return result
endfunc

define var numbers: list = [-2, 0, 5]
define var positives: list = []
filter is_positive numbers positives
```

An explicit function result can be assigned with
`func call <name> [arguments] -> <destination>`.

## Existing built-ins

The interpreter also supports `all`, `any`, `bool`, `callable`, `id`, `len`,
`type`, `vars`, `bin`, `divmod`, `hex`, `oct`, `pow`, `convert`, `bytes`,
`bytearray`, `getattr`, `hasattr`, `setattr`, and `open`. Arithmetic commands
use `arith <operation> <value>` or `arith <operation> <value1> <value2>`.
