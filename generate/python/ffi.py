# -* coding: utf-8 -*

"""
This module generate the Python interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from .constants import BEGINING
from .convert import type_to_python

from generate.ctype import StringType
from generate import CHFL_TYPES

BEGINING += """
# flake8: noqa
'''
Foreign function interface declaration for the Python interface to chemfiles
'''
from numpy.ctypeslib import ndpointer
import numpy as np
from ctypes import c_int, c_uint64, c_double, c_char, c_char_p, c_void_p, c_bool
from ctypes import CFUNCTYPE, ARRAY, POINTER, Structure

from ._utils import _check_return_code
"""

HAND_WRITTEN_TYPES = """
# Some hand-defined type. Make sure to edit the bindgen code to make this
# correspond to the current chemfiles.h header
chfl_vector3d = ARRAY(c_double, 3)

chfl_warning_callback = CFUNCTYPE(None, c_char_p)

class chfl_match(Structure):
    _fields_ = [
        ('size', c_uint64),
        ('atoms', ARRAY(c_uint64, 4))
    ]

# end of hand-defined types
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
    """Convert a function interface to Ctypes"""
    args = [type_to_python(arg.type, argument=True) for arg in function.args]
    argtypes = "[" + ", ".join(args) + "]"
    restype = type_to_python(function.rettype)

    if restype == "chfl_status":
        errcheck = "    c_lib." + function.name
        errcheck += ".errcheck = _check_return_code\n"
    else:
        errcheck = ""
    return FUNCTION_TEMPLATE.format(
        name=function.name,
        coord=function.coord,
        argtypes=argtypes,
        restype=restype,
        errcheck=errcheck,
    )


def wrap_enum(enum):
    """Wrap an enum"""
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

        for name in CHFL_TYPES:
            fd.write(CLASS_TEMPLATE.format(name=name))

        fd.write(HAND_WRITTEN_TYPES)

        fd.write("\n\ndef set_interface(c_lib):")
        fd.write("\n    from chemfiles import Atom")
        fd.write("\n    from chemfiles import Residue")
        fd.write("\n    from chemfiles import Topology")
        fd.write("\n    from chemfiles import UnitCell")
        fd.write("\n    from chemfiles import Frame")
        fd.write("\n    from chemfiles import Selection")
        fd.write("\n    from chemfiles import Trajectory\n")
        fd.write("\n    from chemfiles import Property\n")

        fd.write("\n    # Manually defined functions")
        fd.write("\n    c_lib.chfl_free.argtypes = [c_void_p]")
        fd.write("\n    c_lib.chfl_trajectory_close.argtypes = [Trajectory]")
        fd.write("\n    # End of manually defined functions")
        fd.write("\n")

        for func in functions:
            if func.name in ["chfl_free", "chfl_trajectory_close"]:
                continue
            fd.write(interface(func))
