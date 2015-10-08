# -* coding: utf-8 -*

"""
This module create the fortran version of C arguments, types, ...
"""

from generate.ctype import *
from generate.functions import TYPES

CONVERSIONS = {
    "float": "real(kind=c_float)",
    "double": "real(kind=c_double)",
    "size_t": "integer(kind=c_size_t)",
    "int": "integer(kind=c_int)",
    "bool": "logical(kind=c_bool)",
}

CHFL_TYPES_TO_FORTRAN_INTERFACE = {
    "CHFL_ATOM": "class(chfl_atom)",
    "CHFL_TRAJECTORY": "class(chfl_trajectory)",
    "CHFL_FRAME": "class(chfl_frame)",
    "CHFL_CELL": "class(chfl_cell)",
    "CHFL_TOPOLOGY": "class(chfl_topology)",

    # Enums wrapped to Fortran
    "chfl_cell_type_t":
    'integer(kind=kind(CHFL_CELL_TYPES))',
    "chfl_log_level_t":
    'integer(kind=kind(CHFL_LOG_LEVEL))',
    "chfl_atom_type_t":
    'integer(kind=kind(CHFL_ATOM_TYPES))',
}

# Converting chemfiles types for the c functions declarations
CHFL_TYPES_TO_C_DECLARATIONS = {
    "CHFL_ATOM": "type(c_ptr), value",
    "CHFL_TRAJECTORY": "type(c_ptr), value",
    "CHFL_FRAME": "type(c_ptr), value",
    "CHFL_CELL": "type(c_ptr), value",
    "CHFL_TOPOLOGY": "type(c_ptr), value",

    "chfl_cell_type_t": "integer(kind=c_int)",
    "chfl_log_level_t": "integer(kind=c_int)",
    "chfl_atom_type_t": "integer(kind=c_int)",
}


def type_to_fortran(typ, cdef=False, interface=False):
    if isinstance(typ, StringType):
        return string_to_fortran(typ, cdef=cdef, interface=interface)
    elif isinstance(typ, ArrayType):
        return array_to_fortran(typ, cdef=cdef, interface=interface)
    else:
        return ctype_to_fortran(typ, cdef=cdef, interface=interface)


def ctype_to_fortran(typ, cdef=False, interface=False):
    conversions = CONVERSIONS.copy()
    if cdef:
        conversions.update(CHFL_TYPES_TO_C_DECLARATIONS)
    elif interface:
        conversions.update(CHFL_TYPES_TO_FORTRAN_INTERFACE)
    res = conversions[typ.cname]
    if not typ.is_ptr:
        res += ", value"
    if typ.is_const:
        res += ", intent(in)"
    return res


def string_to_fortran(typ, cdef=False, interface=False):
    if cdef:
        res = "character(len=1, kind=c_char), dimension(*)"
    elif interface:
        res = "character(len=*)"
    if not typ.is_ptr:
        res += ", value"
    if typ.is_const:
        res += ", intent(in)"
    return res


def array_to_fortran(typ, cdef=False, interface=False):
    if cdef:
        return "type(c_ptr), value"
    elif interface:
        res = ctype_to_fortran(typ)
        res += ", dimension("
        if typ.unknown:
            res += ", ".join([":" for i in range(len(typ.all_dims))])
        else:
            res += ", ".join(map(str, typ.all_dims))
        res += "), target"
        return res


def arg_to_fortran(argument, cdef=False, interface=False):
    res = "    " + type_to_fortran(argument.type,
                                   cdef=cdef,
                                   interface=interface)
    res += " :: " + argument.name
    return res


def enum_to_fortran(enum):
    res = ""
    for e in enum.enumerators:
        res += "    enumerator :: " + e.name
        if e.value is not None:
            res += " = " + e.value.value
        res += "\n"
    res += "    ! Enumeration name:\n"
    res += "    enumerator :: " + enum.name
    return res


def function_name_to_fortran(function):
    if function.is_constructor:
        return function.name + "_init_"
    else:
        return function.name
