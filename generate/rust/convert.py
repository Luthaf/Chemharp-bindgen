# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import *

CONVERSIONS = {
    "float": "c_float",
    "double": "c_double",
    "bool": "c_bool",
    "char": "c_char",
    "uint64_t": "uint64_t",
    "int64_t": "int64_t",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_SELECTION": "CHFL_SELECTION",
    "CHFL_RESIDUE": "CHFL_RESIDUE",

    "chfl_cell_shape_t": "CHFL_CELL_SHAPE",
    "chfl_log_level_t": "CHFL_LOG_LEVEL",
    "chfl_match_t": "chfl_match_t",
    "chfl_vector_t": "chfl_vector_t",
    "chfl_status": "chfl_status",

    "chfl_logging_cb": "chfl_logging_callback_t"
}


def type_to_rust(typ):
    if isinstance(typ, StringType):
        return "*const c_char"
    elif isinstance(typ, ArrayType):
        return array_to_rust(typ)
    else:
        if typ.is_ptr:
            const = "const" if typ.is_const else "mut"
            return "*" + const + " " + CONVERSIONS[typ.cname]
        else:
            return CONVERSIONS[typ.cname]


def array_to_rust(typ):
    res = ""
    if isinstance(typ, PtrToArrayType) or -1 not in typ.all_dims:
        res += "*mut "

    for dim in typ.all_dims:
        if dim == -1:
            res += "*mut "
        else:
            res += "["
    res += CONVERSIONS[typ.cname]
    for dim in typ.all_dims:
        if dim != -1:
            res += "; " + str(dim) + "]"
    return res
