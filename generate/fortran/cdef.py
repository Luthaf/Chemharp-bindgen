# -* coding: utf-8 -*

"""
This module generate the Fortran interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from .constants import BEGINING
from .convert import arg_to_fortran

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

ENUMS = {
    "chfl_atom_type_t": "CHFL_ATOM_TYPES",
    "chfl_log_level_t": "CHFL_LOG_LEVEL",
    "chfl_cell_type_t": "CHFL_CELL_TYPES"
}


def interface(function):
    args = ", ".join(map(str, function.args))
    if function.rettype.is_ptr:
        rettype = "type(c_ptr)"
    else:
        rettype = "integer(c_int)"

    imports = ""
    for arg in function.args:
        name = arg.type.cname
        if name in ENUMS.keys():
            imports += "import " + ENUMS[name]

    declarations = "\n".join(
        [arg_to_fortran(arg, cdef=True) for arg in function.args]
    )
    return TEMPLATE.format(name=function.name + "_c",
                           cname=function.name,
                           args=args,
                           coord=function.coord,
                           imports=imports,
                           rettype=rettype,
                           declarations=declarations)


def write_cdef(filename, functions):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        for func in functions:
            fd.write(interface(func))
        fd.write(END)
