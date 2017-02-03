# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import StringType, ArrayType, PtrToArrayType
from generate import CHFL_TYPES

CONVERSIONS = {
    "float": "float",
    "double": "double",
    "size_t": "long",  # FIXME: use a proper size_t mapping
    "int": "int",
    "bool": "bool",
    "char": "byte",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_SELECTION": "CHFL_SELECTION",

    "chfl_cell_type_t": "int",
    "chfl_log_level_t": "int",
    "chfl_atom_type_t": "int",

    "chfl_logging_cb": "LoggingCallback",

    "float*": "FloatByReference",
    "double*": "DoubleByReference",
    "size_t*": "LongByReference",  # FIXME: use a proper size_t mapping
    "bool*": "IntByReference",
    "int*": "IntByReference",

    "chfl_cell_type_t*": "IntByReference",
    "chfl_log_level_t*": "IntByReference",
    "chfl_atom_type_t*": "IntByReference",
}


def type_to_java(typ, cdef=False, interface=False):
    if isinstance(typ, StringType):
        if typ.is_const:
            return "String"
        else:
            return "byte[]"
    elif isinstance(typ, ArrayType):
        return array_to_java(typ, cdef=cdef, interface=interface)
    else:
        if typ.is_ptr:
            if typ.cname in CHFL_TYPES:
                return "Pointer"
            else:
                return CONVERSIONS[typ.cname + "*"]
        else:
            return CONVERSIONS[typ.cname]


def array_to_java(typ, cdef=False, interface=False):
    if isinstance(typ, PtrToArrayType):
        return 'PointerByReference'
    elif typ.cname == "chfl_match_t":
        return "Match"
    else:
        return CONVERSIONS[typ.cname] + '[]'
