# HyperLang TODO — 1.1 Release

## Built-in Functions

### Basic Utilities

* [x] `all()`
* [x] `any()`
* [x] `bool()`
* [x] `callable()`
* [x] `id()`
* [x] `len()`
* [x] `type()`
* [x] `vars()`

### Number & Math Functions

* [x] `bin()`
* [x] `divmod()`
* [x] `hex()`
* [x] `oct()`
* [x] `pow()`

### Type Conversion

* [x] `float()` (via `convert <var> to float`)
* [x] `int()` (via `convert <var> to int`)
* [x] `str()` (via `convert <var> to string`)
* [x] `list()` (via `convert <var> to list`)
* [x] `set()` (via `convert <var> to set`)
* [x] `tuple()` (via `convert <var> to tuple`)

### Character & String Utilities

* [ ] `ascii()`
* [ ] `chr()`
* [ ] `ord()`
* [ ] `format()`
* [ ] `repr()`

### Iteration & Collections

* [ ] `enumerate()`
* [ ] `filter()`
* [ ] `iter()`
* [ ] `map()`
* [ ] `next()`
* [ ] `range()`
* [ ] `reversed()`
* [ ] `slice()`
* [ ] `sorted()`
* [ ] `zip()`

### Collection Types

* [x] Dictionaries / maps
* [x] Sets
* [x] Tuples

### Input & Output

* [x] `open()`

### Object & Attribute Utilities

* [x] `getattr()`
* [x] `hasattr()`
* [x] `setattr()`

### Byte & Binary Data

* [x] `bytes()`
* [x] `bytearray()`

## Language Improvements

* [ ] Better error messages
* [x] More consistent type checking
* [ ] Better function argument handling
* [x] Improved collection handling
* [ ] Improved string handling
* [ ] Built-in function documentation
* [ ] 1.1 example programs
* [ ] 1.1 documentation
* [x] 1.1 regression testing

## 1.1 Quality Checks

* [x] Verify every new built-in works with supported HyperLang types
* [x] Verify invalid arguments produce useful runtime errors
* [x] Verify built-ins do not unexpectedly modify user data
* [x] Verify built-ins work inside functions and loops
* [x] Verify built-ins work together
* [ ] Test large and empty collections
* [ ] Test invalid type conversions
* [ ] Test edge cases for numeric functions
* [ ] Test nested function calls
* [x] Test built-ins with user-defined functions