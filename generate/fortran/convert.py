# -* coding: utf-8 -*
"""
This module create the fortran version of C arguments, types, ...
"""
from generate.ctype import ArrayType, StringType, PtrToArrayType

CONVERSIONS = {
    "double": "real(kind=c_double)",
    "uint64_t": "integer(kind=c_int64_t)",
    # "int": "integer(kind=c_int)",
    "bool": "logical(kind=c_bool)",
    "char": "character",

    "chfl_cellshape": 'integer(chfl_cellshape)',
    "chfl_property_kind": 'integer(chfl_property_kind)',
    "chfl_status": "integer(chfl_status)",

    "chfl_match": "type(chfl_match)",
    "chfl_vector3d": "real(kind=c_double), dimension(3)"
}

CHFL_TYPES_TO_FORTRAN_INTERFACE = {
    "CHFL_ATOM": "class(chfl_atom)",
    "CHFL_RESIDUE": "class(chfl_residue)",
    "CHFL_TOPOLOGY": "class(chfl_topology)",
    "CHFL_CELL": "class(chfl_cell)",
    "CHFL_FRAME": "class(chfl_frame)",
    "CHFL_TRAJECTORY": "class(chfl_trajectory)",
    "CHFL_SELECTION": "class(chfl_selection)",
    "CHFL_PROPERTY": "class(chfl_property)",
    "chfl_warning_callback": "procedure(chfl_warning_callback)"
}

# Converting chemfiles types for the c functions declarations
CHFL_TYPES_TO_C_DECLARATIONS = {
    "CHFL_ATOM": "type(c_ptr), value",
    "CHFL_RESIDUE": "type(c_ptr), value",
    "CHFL_TOPOLOGY": "type(c_ptr), value",
    "CHFL_CELL": "type(c_ptr), value",
    "CHFL_FRAME": "type(c_ptr), value",
    "CHFL_TRAJECTORY": "type(c_ptr), value",
    "CHFL_SELECTION": "type(c_ptr), value",
    "CHFL_PROPERTY": "type(c_ptr), value",
    "chfl_warning_callback": "type(c_funptr)"
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

    by_value = (
        not typ.is_ptr and typ.cname != "chfl_vector3d"
        and not (interface and typ.is_optional)
    )

    if by_value:
        res += ", value"
    if typ.is_const:
        res += ", intent(in)"
    if typ.is_optional and interface:
        res += ", optional"
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
    if typ.is_optional and interface:
        res += ", optional"
    return res


def array_to_fortran(typ, cdef=False, interface=False):
    if cdef:
        return "type(c_ptr), value"
    elif interface:
        if typ.cname == "chfl_vector3d":
            res = "real(kind=c_double)"
            res += ", dimension("
            if typ.unknown_dims:
                res += ":, "
            else:
                res += "3 ,"
        else:
            res = ctype_to_fortran(typ)
            res += ", dimension("
        if typ.unknown_dims:
            res += ", ".join([":" for i in range(len(typ.all_dims))])
        else:
            res += ", ".join(map(str, typ.all_dims))
        res += ")"
        if isinstance(typ, PtrToArrayType):
            res += ", pointer"
        else:
            res += ", target"

        if typ.is_optional and interface:
            res += ", optional"
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
        res += "\n    enumerator :: " + e.name
        if e.value is not None:
            res += " = " + e.value.value
    return res


def function_name_to_fortran(function):
    if function.is_constructor:
        return function.name + "_init_"
    else:
        return function.name
