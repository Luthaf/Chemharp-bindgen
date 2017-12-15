# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import ArrayType, StringType, PtrToArrayType
from generate import CHFL_TYPES

CONVERSIONS = {
    "double": "c_double",
    "uint64_t": "c_uint64",
    "bool": "c_bool",
    "char": "c_char",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_RESIDUE": "CHFL_RESIDUE",
    "CHFL_SELECTION": "CHFL_SELECTION",
    "CHFL_PROPERTY": "CHFL_PROPERTY",

    "chfl_status": "chfl_status",
    "chfl_cellshape": "chfl_cellshape",
    "chfl_property_kind": "chfl_property_kind",

    "chfl_vector3d": "chfl_vector3d",
    "chfl_warning_callback": "chfl_warning_callback"
}

NUMPY_CONVERSIONS = {
    "double": "np.float64",
    "uint64_t": "np.uint64",
    "bool": "np.bool",
    "chfl_match": "chfl_match",
    "chfl_vector3d": "chfl_vector3d",
}

CHFL_TYPE_CONVERSIONS = {
    "CHFL_ATOM": "Atom",
    "CHFL_TRAJECTORY": "Trajectory",
    "CHFL_FRAME": "Frame",
    "CHFL_CELL": "UnitCell",
    "CHFL_TOPOLOGY": "Topology",
    "CHFL_RESIDUE": "Residue",
    "CHFL_SELECTION": "Selection",
    "CHFL_PROPERTY": "Property",
}


def type_to_python(typ, argument=False):
    if isinstance(typ, StringType):
        return "c_char_p"
    elif isinstance(typ, ArrayType):
        return array_to_python(typ)
    else:
        if typ.is_ptr:
            if argument and typ.cname in CHFL_TYPES:
                return CHFL_TYPE_CONVERSIONS[typ.cname]
            else:
                return "POINTER(" + CONVERSIONS[typ.cname] + ")"
        else:
            return CONVERSIONS[typ.cname]


def array_to_python(typ):
    if isinstance(typ, PtrToArrayType):
        ctype = CONVERSIONS[typ.cname]
        res = 'POINTER(POINTER(' + ctype + '))'
    elif typ.unknown_dims:
        ctype = NUMPY_CONVERSIONS[typ.cname]
        res = 'ndpointer(' + ctype + ', flags="C_CONTIGUOUS"'
        res += ', ndim=' + str(len(typ.all_dims))
        res += ')'
    else:
        ctype = CONVERSIONS[typ.cname]
        shape = ", ".join(typ.all_dims)
        res = 'ARRAY(' + ctype + ', (' + shape + '))'

    return res
