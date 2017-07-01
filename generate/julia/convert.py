# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import StringType, ArrayType, PtrToArrayType

CONVERSIONS = {
    "double": "Cdouble",
    "bool": "Cbool",
    "char": "Cchar",
    "uint64_t": "UInt64",
    "int64_t": "Int64",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_RESIDUE": "CHFL_RESIDUE",
    "CHFL_SELECTION": "CHFL_SELECTION",

    "chfl_cell_shape_t": "chfl_cell_shape_t",
    "chfl_match_t": "chfl_match_t",
    "chfl_vector_t": "chfl_vector_t",

    "chfl_status": "chfl_status",
    "chfl_warning_callback": "Ptr{Void}",
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
    # Pointers to chfl_vector_t should just be pointers to Float64
    if ctype == "chfl_vector_t":
        ctype = "Float64"
    if isinstance(typ, PtrToArrayType):
        res = 'Ref{Ptr{' + ctype + '}}'
    else:
        res = 'Ptr{' + ctype + '}'
    return res
