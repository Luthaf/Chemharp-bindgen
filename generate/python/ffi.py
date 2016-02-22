# -* coding: utf-8 -*

"""
This module generate the Python interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from .constants import BEGINING
from .convert import type_to_python

from generate.ctype import StringType
from generate.functions import TYPES

BEGINING += """
# flake8: noqa
'''
Foreign function interface declaration for the Python interface to chemfiles
'''
from numpy.ctypeslib import ndpointer
import numpy as np
from ctypes import *

from .errors import _check_return_code
"""

CHFL_LOGGING_CALLBACK = """

chfl_logging_callback_t = CFUNCTYPE(None, CHFL_LOG_LEVEL, c_char_p)
"""

CLASS_TEMPLATE = """

class {name}(Structure):
    pass
"""

ENUM_TEMPLATE = """

class {name}(c_int):
    {values}
"""

FUNCTION_TEMPLATE = """
    # Function "{name}", at {coord}
    c_lib.{name}.argtypes = {argtypes}
    c_lib.{name}.restype = {restype}
{errcheck}"""


def interface(function):
    '''Convert a function interface to Ctypes'''
    args = [type_to_python(arg.type, cdef=True) for arg in function.args]
    argtypes = "[" + ", ".join(args) + "]"
    restype = type_to_python(function.rettype)

    if restype == "c_int":
        errcheck = "    c_lib." + function.name
        errcheck += ".errcheck = _check_return_code\n"
    else:
        errcheck = ""
    return FUNCTION_TEMPLATE.format(name=function.name,
                                    coord=function.coord,
                                    argtypes=argtypes,
                                    restype=restype,
                                    errcheck=errcheck)


def wrap_enum(enum):
    '''Wrap an enum'''
    values = []
    i = 0
    for e in enum.enumerators:
        if e.value is None:
            value = i
            i += 1
        else:
            value = e.value.value
        values.append(str(e.name) + " = " + str(value))
    return ENUM_TEMPLATE.format(name=enum.name, values="\n    ".join(values))


def write_ffi(filename, enums, functions):
    with open(filename, "w") as fd:
        fd.write(BEGINING)

        for enum in enums:
            fd.write(wrap_enum(enum))

        for name in TYPES:
            fd.write(CLASS_TEMPLATE.format(name=name))

        fd.write(CHFL_LOGGING_CALLBACK)

        fd.write("\n\ndef set_interface(c_lib):")
        for func in functions:
            fd.write(interface(func))
