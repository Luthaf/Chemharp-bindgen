# -* coding: utf-8 -*
"""
This module generate the Fortran interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
import os
from .constants import BEGINING, FORTRAN_TYPES
from .convert import type_to_fortran

BEGINING += "interface\n"
END = "end interface\n"

TEMPLATE = """! Function "{cname}", at {coord}
function {name}({args}) bind(C, name="{cname}")
    use iso_c_binding
    {imports}
    implicit none
    {rettype} :: {name}
{declarations}
end function\n
"""

ENUMS = [
    "chfl_status", "chfl_cellshape", "chfl_bond_order", "chfl_property_kind"
]


def interface(function):
    args = ", ".join(map(str, function.args))
    if function.rettype.is_ptr:
        imports = ""
        rettype = "type(c_ptr)"
    else:
        imports = "import chfl_status\n"
        rettype = "integer(kind=chfl_status)"

    for arg in function.args:
        name = arg.type.cname
        if name in ENUMS:
            imports += "    import " + name + "\n"

    declarations = "\n".join([
        "    {} :: {}".format(type_to_fortran(arg.type), arg.name)
        for arg in function.args
    ])

    return TEMPLATE.format(
        name="c_" + function.name,
        cname=function.name,
        args=args,
        coord=function.coord,
        imports=imports,
        rettype=rettype,
        declarations=declarations,
    )


def write_definitions(root, functions):
    for type in FORTRAN_TYPES:
        with open(os.path.join(root, type + ".f90"), "w") as fd:
            fd.write(BEGINING)
            for function in functions:
                if function.name.startswith(type):
                    fd.write(interface(function))
            fd.write(END)

    others = []
    for function in functions:
        name = "_".join(function.name.split("_")[:2])
        if name not in FORTRAN_TYPES and name != "chfl_free":
            others.append(function)

    with open(os.path.join(root, "others.f90"), "w") as fd:
        fd.write(BEGINING)
        for function in others:
            fd.write(interface(function))
        fd.write(END)
