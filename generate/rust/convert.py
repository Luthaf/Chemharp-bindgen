# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import StringType, ArrayType, PtrToArrayType

CONVERSIONS = {
    "double": "c_double",
    "bool": "c_bool",
    "char": "c_char",
    "uint64_t": "u64",
    "void": "c_void",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_SELECTION": "CHFL_SELECTION",
    "CHFL_RESIDUE": "CHFL_RESIDUE",
    "CHFL_PROPERTY": "CHFL_PROPERTY",

    "chfl_cellshape": "chfl_cellshape",
    "chfl_property_kind": "chfl_property_kind",
    "chfl_bond_order": "chfl_bond_order",
    "chfl_match": "chfl_match",
    "chfl_status": "chfl_status",

    "chfl_warning_callback": "chfl_warning_callback"
}


def type_to_rust(typ):
    if isinstance(typ, StringType):
        if typ.is_const:
            return "*const c_char"
        else:
            return "*mut c_char"
    elif isinstance(typ, ArrayType):
        return array_to_rust(typ)
    elif typ.cname == "chfl_vector3d":
        const = "const" if typ.is_const else "mut"
        return "*" + const + " c_double"
    else:
        if typ.is_ptr:
            const = "const" if typ.is_const else "mut"
            return "*" + const + " " + CONVERSIONS[typ.cname]
        else:
            return CONVERSIONS[typ.cname]


def array_to_rust(typ):
    res = ""
    if isinstance(typ, PtrToArrayType):
        if typ.cname == "chfl_vector3d":
            assert typ.ctype.type.type.declname in ["positions", "velocities"]
            return "*mut *mut [c_double; 3]"
        else:
            assert typ.cname == "char"
            return "*mut *mut c_char"

    if -1 not in typ.all_dims:
        res += "*mut "

    for dim in typ.all_dims:
        if dim == -1:
            res += "*mut "
        else:
            res += "["

    if typ.cname == "chfl_vector3d":
        res += "c_double"
    else:
        res += CONVERSIONS[typ.cname]
    for dim in typ.all_dims:
        if dim != -1:
            res += "; " + str(dim) + "]"
    return res
