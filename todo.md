# HyperLang TODO — 1.1 Release

## Built-in Functions

### Basic Utilities

* [ ] `all()`
* [ ] `any()`
* [ ] `bool()`
* [ ] `callable()`
* [ ] `id()`
* [ ] `len()`
* [ ] `type()`
* [ ] `vars()`

### Number & Math Functions

* [x] `bin()`
* [x] `divmod()`
* [x] `hex()`
* [x] `oct()`
* [x] `pow()`

### Type Conversion

* [ ] `float()`
* [ ] `int()`
* [ ] `str()`
* [ ] `list()`
* [ ] `set()`
* [ ] `tuple()`

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

* [ ] Dictionaries / maps
* [ ] Sets
* [ ] Tuples

### Input & Output

* [ ] `open()`

### Object & Attribute Utilities

* [ ] `getattr()`
* [ ] `hasattr()`
* [ ] `setattr()`

### Byte & Binary Data

* [ ] `bytes()`
* [ ] `bytearray()`

## Language Improvements

* [ ] Better error messages
* [ ] More consistent type checking
* [ ] Better function argument handling
* [ ] Improved collection handling
* [ ] Improved string handling
* [ ] Built-in function documentation
* [ ] 1.1 example programs
* [ ] 1.1 documentation
* [ ] 1.1 regression testing

## 1.1 Quality Checks

* [ ] Verify every new built-in works with supported HyperLang types
* [ ] Verify invalid arguments produce useful runtime errors
* [ ] Verify built-ins do not unexpectedly modify user data
* [ ] Verify built-ins work inside functions and loops
* [ ] Verify built-ins work together
* [ ] Test large and empty collections
* [ ] Test invalid type conversions
* [ ] Test edge cases for numeric functions
* [ ] Test nested function calls
* [ ] Test built-ins with user-defined functions