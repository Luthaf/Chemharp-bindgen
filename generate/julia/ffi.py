# -* coding: utf-8 -*

"""
This module generate the Julia interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from generate.julia.constants import BEGINING
from generate.julia.convert import type_to_julia
from generate import CHFL_TYPES


TYPE_TEMPLATE = """
immutable {name} end
"""

ENUM_TEMPLATE = """# enum {name}
typealias {name} UInt32
{values}
"""

FUNCTION_TEMPLATE = """
# Function '{name}' at {coord}
function {name}({argdecl})
    ccall((:{name}, libchemfiles), {restype}, {argtypes}, {args})
end
"""

MANUAL_TYPES = """
# === Manually translated from the header
immutable chfl_match_t
    size    ::UInt64
    atoms_1 ::UInt64
    atoms_2 ::UInt64
    atoms_3 ::UInt64
    atoms_4 ::UInt64
end

typealias Cbool Cuchar
typealias chfl_vector_t Array{Cdouble, 1}
# === End of manual translation
"""


def wrap_enum(enum):
    '''Wrap an enum'''
    typename = enum.name
    values = ""
    for enumerator in enum.enumerators:
        values += "const " + str(enumerator.name) + " = "
        values += typename + "(" + str(enumerator.value.value) + ")\n"
    return ENUM_TEMPLATE.format(name=typename, values=values[:-1])


def write_types(filename, enums):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        fd.write(MANUAL_TYPES)

        for name in CHFL_TYPES:
            fd.write(TYPE_TEMPLATE.format(name=name))

        for enum in enums:
            fd.write("\n")
            fd.write(wrap_enum(enum))


def write_functions(filename, functions):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        for func in functions:
            fd.write(interface(func))


def interface(function):
    '''Convert a function interface to Julia'''
    names = [arg.name for arg in function.args]
    types = [type_to_julia(arg.type) for arg in function.args]

    # Filter arguments named 'type'
    names = [n if n != "type" else "typ" for n in names]

    args = ", ".join(names)
    argdecl = ", ".join(n + "::" + t for (n, t) in zip(names, types))

    # Filter arguments for ccall
    types = [t if t != "chfl_vector_t" else "Ptr{Float64}" for t in types]
    if len(types) == 0:
        argtypes = "()"  # Empty tuple
    elif len(types) == 1:
        argtypes = "(" + types[0] + ",)"
    else:
        argtypes = "(" + ", ".join(types) + ")"

    restype = type_to_julia(function.rettype)

    if restype == "c_int":
        errcheck = "    c_lib." + function.name
        errcheck += ".errcheck = _check_return_code\n"
    else:
        errcheck = ""
    return FUNCTION_TEMPLATE.format(name=function.name,
                                    coord=function.coord,
                                    argtypes=argtypes,
                                    args=args,
                                    argdecl=argdecl,
                                    restype=restype,
                                    errcheck=errcheck)
