# -* coding: utf-8 -*

"""
This module generate the Rust interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from generate.js.constants import BEGINING
from generate.js.convert import type_to_js
from generate import CHFL_TYPES

TYPE_TEMPLATE = " +\n    'struct {name} {{}};'"
FUNCTION_TEMPLATE = " +\n    '{rettype} {name}({args});'"
ENUM_TEMPLATE = "\nvar {name} = {{{values}}}\n"

REQUIRE = """
const fastcall = require('fastcall');
const Library = fastcall.Library;

const find_lib = require('./find_lib');
"""

MANUAL_TYPES = """
    // Manually defined types. Please triple check that they match the
    // definition in chemfiles.h
    'void (*chfl_warning_callback)(char* message);' +
    'double[3] chfl_vector3d;' +
    'struct chfl_match {uint64 size; uint64 atoms[4];};' +
    // End of manual definitions
    ''"""


def wrap_enum(enum):
    typename = enum.name
    values = "\n"
    for enumerator in enum.enumerators:
        values += "    {name}: {value},\n".format(
            name=enumerator.name,
            value=enumerator.value.value,
        )
    return ENUM_TEMPLATE.format(name=typename, values=values)


def wrap_function(function):
    names = [arg.name for arg in function.args]
    types = [type_to_js(arg.type) for arg in function.args]
    args = ", ".join(t + " " + n for (t, n) in zip(types, names))

    rettype = type_to_js(function.rettype)
    return FUNCTION_TEMPLATE.format(
        name=function.name,
        args=args,
        rettype=rettype
    )


def write_ffi(filename, ffi):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        fd.write(REQUIRE)

        for enum in ffi.enums:
            fd.write(wrap_enum(enum))

        fd.write("\nconst lib = new Library(find_lib()).declare(")
        fd.write(MANUAL_TYPES)

        for name in CHFL_TYPES:
            fd.write(TYPE_TEMPLATE.format(name=name))

        for function in ffi.functions:
            fd.write(wrap_function(function))

        fd.write("\n);")
