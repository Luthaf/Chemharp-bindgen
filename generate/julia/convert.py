# -* coding: utf-8 -*
"""
This module create the julia version of C arguments, types, ...
"""
from generate.ctype import StringType, ArrayType, PtrToArrayType

CONVERSIONS = {
    "double": "Cdouble",
    "bool": "Cbool",
    "char": "Cchar",
    "uint64_t": "UInt64",
    "void": "Cvoid",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_RESIDUE": "CHFL_RESIDUE",
    "CHFL_SELECTION": "CHFL_SELECTION",
    "CHFL_PROPERTY": "CHFL_PROPERTY",

    "chfl_vector3d": "chfl_vector3d",

    "chfl_cellshape": "chfl_cellshape",
    "chfl_bond_order": "chfl_bond_order",
    "chfl_property_kind": "chfl_property_kind",
    "chfl_match": "chfl_match",
    "chfl_status": "chfl_status",

    "chfl_status": "chfl_status",
    "chfl_warning_callback": "Ptr{Cvoid}",
}


def type_to_julia(typ):
    if isinstance(typ, StringType):
        return "Ptr{UInt8}"
    elif isinstance(typ, ArrayType):
        if typ.cname == "char":
            return "Ptr{Ptr{UInt8}}"
        else:
            return array_to_julia(typ)
    else:
        if typ.is_ptr:
            if typ.cname.startswith("CHFL_") or typ.cname == "void":
                return "Ptr{" + CONVERSIONS[typ.cname] + "}"
            else:
                return "Ref{" + CONVERSIONS[typ.cname] + "}"

        else:
            return CONVERSIONS[typ.cname]


def array_to_julia(typ):
    ctype = CONVERSIONS[typ.cname]
    # Pointers to chfl_vector3d should just be pointers to Float64
    if ctype == "chfl_vector3d":
        ctype = 'Cdouble'
    if isinstance(typ, PtrToArrayType):
        res = 'Ref{Ptr{' + ctype + '}}'
    else:
        res = 'Ptr{' + ctype + '}'
    return res
