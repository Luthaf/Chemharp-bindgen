# -* coding: utf-8 -*
"""
This module create the fortran version of C arguments, types, ...
"""
from generate.ctype import ArrayType, StringType
from generate import CHFL_TYPES

CONVERSIONS = {
    "double": "real(kind=c_double)",
    "uint64_t": "integer(kind=c_int64_t)",
    "int64_t": "integer(kind=c_int64_t)",
    "bool": "logical(kind=c_bool)",
    "char": "character",
    "chfl_cellshape": "integer(chfl_cellshape)",
    "chfl_property_kind": "integer(chfl_property_kind)",
    "chfl_status": "integer(chfl_status)",
    "chfl_bond_order": "integer(chfl_bond_order)",
    "chfl_match": "type(chfl_match)",
    "chfl_vector3d": "real(kind=c_double), dimension(3)",
    "chfl_warning_callback": "type(c_funptr)",
}


def type_to_fortran(typ):
    if isinstance(typ, StringType):
        return string_to_fortran(typ)
    elif isinstance(typ, ArrayType):
        return "type(c_ptr), value"
    else:
        return ctype_to_fortran(typ)


def ctype_to_fortran(typ):
    if typ.cname in CHFL_TYPES:
        if typ.is_const:
            return "type(c_ptr), value, intent(in)"
        else:
            return "type(c_ptr), value"

    res = CONVERSIONS[typ.cname]

    if not typ.is_ptr and typ.cname != "chfl_vector3d":
        res += ", value"
    else:
        if typ.is_const:
            res += ", intent(in)"
        else:
            res += ", intent(inout)"
    return res


def string_to_fortran(typ):
    res = "character(len=1, kind=c_char), dimension(*)"
    if typ.is_const:
        res += ", intent(in)"
    return res
