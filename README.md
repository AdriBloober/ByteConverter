# Byte Converter

## Installation

Install python with version >= 3.6 and pip.

Install package with
```shell script
python3 -m pip install --upgrade byte-converter --user
```

## Usage

### Basic types

```python
from byte_converter import to_bytes, read_bytes

int_bytes = to_bytes(int(input("Write a number: ")))
dict_bytes = to_bytes({"a": 13 * 2, "b": "asdf"})
```

### Own object

```python
from byte_converter import to_bytes, read_bytes

class User:
    bc_ignore_attributes = ["this_attribute_will_be_ignored"] # you can use regex also
    this_attribute_will_be_ignored = 13
    def __init__(self, username, password):
        self.username = username
        self.password = password

user = User(input("username: "), input("password: "))
user_in_bytes = to_bytes(user)
user = read_bytes(user_in_bytes, parsable_classes=[User])
```

If you wan't to read objects, you must set a `parsable_classes` argument for reading with a list of readable classes.

### Ignore or whitelist attributes

Set the ``bc_ignore_attributes`` attribute to a list of name of attributes, which will be ignored. (You can use regex).
Set the ``bc_whitelisted_attributes`` attribute to a list of name of attributes. Only these attributes will be saved and all other attributes will be ignored, if you set this attribute to a list.


### Parsable types

These types are parsable

1. ``NoneType``
2. ``bool``
3. ``int``
4. ``float``
5. ``str``
6. ``list``
7. ``dict``
8. Own objects (no built-in objects)