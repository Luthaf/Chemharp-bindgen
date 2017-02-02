# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import ArrayType, StringType, PtrToArrayType

CONVERSIONS = {
    "double": "c_double",
    "uint64_t": "c_uint64",
    "int64_t": "c_int64",
    "bool": "c_bool",
    "char": "c_char",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_RESIDUE": "CHFL_RESIDUE",
    "CHFL_SELECTION": "CHFL_SELECTION",

    "chfl_status": "chfl_status",
    "chfl_cell_shape_t": "chfl_cell_shape_t",

    "chfl_vector_t": "chfl_vector_t",
    "chfl_warning_callback": "chfl_warning_callback"
}

NUMPY_CONVERSIONS = {
    "double": "np.float64",
    "uint64_t": "np.uint64",
    "bool": "np.bool",
    "chfl_match_t": "chfl_match_t",
    "chfl_vector_t": "chfl_vector_t",
}


def type_to_python(typ, cdef=False, interface=False):
    if isinstance(typ, StringType):
        return "c_char_p"
    elif isinstance(typ, ArrayType):
        return array_to_python(typ, cdef=cdef, interface=interface)
    else:
        if typ.is_ptr:
            return "POINTER(" + CONVERSIONS[typ.cname] + ")"
        else:
            return CONVERSIONS[typ.cname]


def array_to_python(typ, cdef=False, interface=False):
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
