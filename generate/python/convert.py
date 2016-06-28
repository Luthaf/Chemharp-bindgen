# -* coding: utf-8 -*
"""
This module create the python version of C arguments, types, ...
"""
from generate.ctype import *

CONVERSIONS = {
    "float": "c_float",
    "double": "c_double",
    "size_t": "c_size_t",
    "int": "c_int",
    "bool": "c_bool",
    "char": "c_char",

    "CHFL_ATOM": "CHFL_ATOM",
    "CHFL_TRAJECTORY": "CHFL_TRAJECTORY",
    "CHFL_FRAME": "CHFL_FRAME",
    "CHFL_CELL": "CHFL_CELL",
    "CHFL_TOPOLOGY": "CHFL_TOPOLOGY",
    "CHFL_SELECTION": "CHFL_SELECTION",

    "chfl_cell_type_t": "c_int",
    "chfl_log_level_t": "c_int",
    "chfl_atom_type_t": "c_int",

    "chfl_logging_cb": "chfl_logging_callback_t"
}

NUMPY_CONVERSIONS = {
    "float": "np.float32",
    "double": "np.float64",
    "size_t": "np.uintp",
    "int": "np.int32",
    "bool": "np.bool",
    "chfl_match_t": "chfl_match_t",
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
    else:
        ctype = NUMPY_CONVERSIONS[typ.cname]
        res = 'ndpointer(' + ctype + ', flags="C_CONTIGUOUS"'
        res += ', ndim=' + str(len(typ.all_dims))
        if not typ.unknown:
            res += ', shape=(' + ", ".join(map(str, typ.all_dims)) + ')'
        res += ')'
    return res
