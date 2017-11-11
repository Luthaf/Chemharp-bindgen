# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import StringType, ArrayType, PtrToArrayType

CONVERSIONS = {
    "double": "double",
    "bool": "bool",
    "char": "char",
    "uint64_t": "uint64",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_SELECTION": "CHFL_SELECTION",
    "CHFL_RESIDUE": "CHFL_RESIDUE",
    "CHFL_PROPERTY": "CHFL_PROPERTY",

    "chfl_cellshape": "int",
    "chfl_property_kind": "int",
    "chfl_match": "chfl_match",
    "chfl_status": "int",
    "chfl_vector3d": "chfl_vector3d",

    "chfl_warning_callback": "chfl_warning_callback"
}


def type_to_js(typ):
    if isinstance(typ, StringType):
        return "char*"
    elif isinstance(typ, ArrayType):
        return array_to_js(typ)
    else:
        name = CONVERSIONS[typ.cname]
        if typ.is_ptr:
            name += "*"
        return name


def array_to_js(typ):
    ctype = CONVERSIONS[typ.cname]
    if ctype == "chfl_vector3d":
        ctype = "double"
    if isinstance(typ, PtrToArrayType):
        res = ctype + '**'
    else:
        res = ctype + '*'
    return res
