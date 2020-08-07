import io
import json
import re
import base64 as b64


def write_bool(boolean: bool, buffer):
    if boolean:
        buffer.write(b"1")
    else:
        buffer.write(b"0")


def write_int(integer: int, buffer):
    length = 0
    integer_bytes = b""
    positive = integer >= 0
    if not positive:
        integer = 0 - integer
    while True:
        length += 1
        try:
            integer_bytes = integer.to_bytes(length, "big")
            break
        except OverflowError:  # integer length is to low
            continue
    write_bool(positive, buffer)
    buffer.write(length.to_bytes(1, "little"))
    buffer.write(integer_bytes)


def write_string(string: str, buffer):
    ending_value = b"\x0f"
    ending_replacement = b"\x0d\x0e"
    s = b""
    for i in string:
        if i.encode("utf-8") == ending_value:
            s += ending_replacement
        else:
            s += i.encode("utf-8")
    s += ending_value
    buffer.write(s)


def write_float(f: float, buffer):
    write_string(f.hex(), buffer)


def parse_dict_value(v):
    if v is None:
        return v
    if type(v) in (str, int, float):
        return v
    elif type(v) == list:
        l = []
        for l_v in v:
            l.append(parse_dict_value(l_v))
        return l
    elif type(v) == dict:
        a = {}
        for k, v in v.items():
            a[k] = parse_dict_value(v)
        return a
    elif hasattr(v, "__class__") and v.__class__ != type:
        o = obj_to_dict(v)
        o["__from__"] = "ctbc"
        return o
    else:
        raise ValueError(f"Value {v} with type {type(v)} is not parsable!")


def write_list(l: list, buffer):
    write_int(len(l), buffer)
    for i in l:
        to_bytes(i, buffer, base64=False)


def write_dict(dictionary: dict, buffer):
    new_dict = {}
    for k, v in dictionary.items():
        new_dict[k] = parse_dict_value(v)
    write_string(json.dumps(new_dict), buffer)


def check_regex_obj(r, attribute_name):
    if r == attribute_name:
        return True
    for _, _ in enumerate(re.finditer(r, attribute_name, re.MULTILINE), start=1):
        return True
    return False


def obj_to_dict(obj):
    dictionary = {}
    ignoring_attributes = ["bc_ignore_attributes", "bc_whitelisted_attributes", r"\_.*"]
    if hasattr(obj, "bc_ignore_attributes"):
        ignoring_attributes.extend(obj.bc_ignore_attributes)
    whitelisting = None
    if hasattr(obj, "bc_whitelisted_attributes"):
        whitelisting = obj.bc_whitelisted_attributes
    for k in dir(obj):
        ignoring = False
        for i in ignoring_attributes:
            if check_regex_obj(i, k):
                ignoring = True
                break
        if not ignoring:
            if whitelisting:
                whitelisted = False
                for w in whitelisting:
                    if check_regex_obj(w, k):
                        whitelisted = True
                        break
                if not whitelisted:
                    continue
            v = getattr(obj, k)
            if not callable(v):
                dictionary[k] = getattr(obj, k)
    dictionary["__class__.__name__"] = obj.__class__.__name__
    return dictionary


def write_object(obj, buffer):
    write_string(obj.__class__.__name__, buffer)
    write_dict(obj_to_dict(obj), buffer)


def write_none(obj, buffer):
    pass


type_definition = {
    b"\x01": (bool, write_bool),
    b"\x02": (int, write_int),
    b"\x03": (float, write_float),
    b"\x04": (str, write_string),
    b"\x05": (list, write_list),
    b"\x06": (dict, write_dict),
    b"\x07": (None, write_none),
}


def to_bytes(obj, buffer=None, base64=True):
    if not buffer:
        buffer = io.BytesIO()
    fount = False
    for k, v in type_definition.items():
        if type(obj) == v[0]:
            buffer.write(k)
            v[1](obj, buffer)
            fount = True
            break
    if obj is None and not fount:
        buffer.write(b"\x07")
    elif not fount:
        buffer.write(b"\x10")
        write_object(obj, buffer)
    b = buffer.getvalue()
    if base64:
        b = b64.b64encode(b)
    return b
