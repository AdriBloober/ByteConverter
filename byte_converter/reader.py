import json
from io import BytesIO
import base64 as b64


def read_bool(buffer):
    v = buffer.read(1)
    return v == b"1"


def read_int(buffer):
    positive = read_bool(buffer)
    int_length = int.from_bytes(buffer.read(1), "little")
    v = int.from_bytes(buffer.read(int_length), "big")
    if not positive:
        v = 0 - v
    return v


def read_string(buffer):
    ending_value = b"\x0f"
    ending_replacement = b"\x0d\x0e"
    s = ""
    while True:
        v = buffer.read(1)
        if v == ending_replacement:
            s += ending_value.decode("utf-8")
        if v == ending_value:
            break
        s += v.decode("utf-8")
    return s


def read_float(buffer):
    return float.fromhex(read_string(buffer))


def read_list(buffer, parsable_classes=None):
    list_length = read_int(buffer)
    l = []
    for i in range(list_length):
        l.append(read_bytes(buffer, parsable_classes=parsable_classes, base64=False))
    return l


def parse_dict_value(v):
    if v is None:
        return v
    if type(v) in (str, int, float):
        return v
    elif type(v) == dict:
        dd = {}
        for k, v in v.items():
            dd[k] = parse_dict_value(v)
        return dd
    elif type(v) == list:
        l = []
        for value in v:
            l.append(parse_dict_value(value))
        return l
    else:
        raise ValueError(f"Value {v} with type {type(v)} is not parsable!")


def read_object_from_dict(d, object_class, parsable_classes=None):
    obj = object_class.__new__(object_class)
    if not parsable_classes:
        parsable_classes = []
    for k, v in d.items():
        if type(v) == dict and "__from__" in v and v["__from__"] == "ctbc":
            f = False
            for c in parsable_classes:
                if c.__name__ == v["__class__.__name__"]:
                    setattr(obj, k, read_object_from_dict(v, c, parsable_classes))
                    f = True
                    break
            if not f:
                raise ValueError(
                    f"Class {v['__class__.__name__']}"
                    f"is not parsable! Please add this class to parsable_classes argument!"
                )
        else:
            setattr(obj, k, parse_dict_value(v))
    return obj


def read_object_from_bytes(object_class, buffer, parsable_classes=None):
    d = read_dict(buffer)
    return read_object_from_dict(d, object_class, parsable_classes=parsable_classes)


def read_dict(buffer):
    d = {}
    for k, v in json.loads(read_string(buffer)).items():
        d[k] = parse_dict_value(v)
    return d


def read_none(buffer):
    return None


type_definition = {
    b"\x01": (bool, read_bool),
    b"\x02": (int, read_int),
    b"\x03": (float, read_float),
    b"\x04": (str, read_string),
    b"\x05": (list, read_list),
    b"\x06": (dict, read_dict),
    b"\x07": (None, read_none),
}


def read_bytes(buffer, parsable_classes=None, base64=True):
    if type(buffer) == bytes:
        if base64:
            buffer = BytesIO(b64.b64decode(buffer))
        else:
            buffer = BytesIO(buffer)
    elif base64:
        buffer = BytesIO(b64.b64decode(buffer.read()))
    if not parsable_classes:
        parsable_classes = []
    if type(parsable_classes) != list:
        parsable_classes = [parsable_classes]
    tr = buffer.read(1)
    t = type_definition.get(tr, None)
    if t:
        if t[1] == read_list:
            return t[1](buffer, parsable_classes=parsable_classes)
        else:
            return t[1](buffer)
    elif tr == b"\x10":
        class_name = read_string(buffer)
        for c in parsable_classes:
            if c.__name__ == class_name:
                return read_object_from_bytes(
                    c, buffer, parsable_classes=parsable_classes
                )
        raise ValueError(
            f"Class {class_name} is not parsable! Please add this class to parsable_classes argument!"
        )
    elif tr is None:
        return None
    else:
        raise ValueError(f"Type {tr} is not parsable!")
