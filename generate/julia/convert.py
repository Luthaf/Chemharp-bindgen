# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import *

CONVERSIONS = {
    "float": "Cfloat",
    "double": "Cdouble",
    "size_t": "Csize_t",
    "int": "Cint",
    "bool": "CBool",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",

    "chfl_cell_type_t": "CHFL_CELL_TYPES",
    "chfl_log_level_t": "CHFL_LOG_LEVEL",
    "chfl_atom_type_t": "CHFL_ATOM_TYPES",

    "chfl_logging_cb": "Ptr{Void}"
}


def type_to_julia(typ):
    if isinstance(typ, StringType):
        return "Ptr{UInt8}"
    elif isinstance(typ, ArrayType):
        return array_to_julia(typ)
    else:
        if typ.is_ptr:
            if not typ.cname.startswith("CHFL_"):
                return "Ref{" + CONVERSIONS[typ.cname] + "}"
            else:
                return "Ptr{" + CONVERSIONS[typ.cname] + "}"
        else:
            return CONVERSIONS[typ.cname]


def array_to_julia(typ):
    ctype = CONVERSIONS[typ.cname]
    if isinstance(typ, PtrToArrayType):
        res = 'Ref{Ptr{' + ctype + '}}'
    else:
        res = 'Ptr{' + ctype + '}'
    return res
