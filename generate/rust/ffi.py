# -* coding: utf-8 -*

"""
This module generate the Rust interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from generate.rust.constants import BEGINING
from generate.rust.convert import type_to_rust
from generate.functions import TYPES

TYPE_TEMPLATE = "pub enum {name}{{}}\n"

ENUM_TEMPLATE = """
// C enum {name}
pub type {name} = c_uint;
{values}
"""

FUNCTION_TEMPLATE = """    pub fn {name}({args}) -> {returns};\n"""

MANUAL_DEFS = """
pub type CHFL_STATUS = c_int;
pub type chfl_logging_callback_t = extern fn(CHFL_LOG_LEVEL, *const c_char);
pub type c_bool = u8;

#[repr(C)]
pub struct chfl_match_t {
    size: c_char,
    atoms: [size_t; 4],
}

// TODO: use an enum here
pub const CHFL_SUCCESS: CHFL_STATUS = 0;
pub const CHFL_MEMORY_ERROR: CHFL_STATUS = 1;
pub const CHFL_FILE_ERROR: CHFL_STATUS = 2;
pub const CHFL_FORMAT_ERROR: CHFL_STATUS = 3;
pub const CHFL_SELECTION_ERROR: CHFL_STATUS = 4;
pub const CHFL_GENERIC_ERROR: CHFL_STATUS = 5;
pub const CHFL_CXX_ERROR: CHFL_STATUS = 6;
"""

EXTERN_START = """
#[link(name="chemfiles", kind="static")]
extern "C" {
"""

EXTERN_END = "}\n"

CRATES = """
#![allow(non_camel_case_types)]
extern crate libc;
use libc::{c_float, c_double, c_char, c_int, c_uint, size_t};

"""


def wrap_enum(enum):
    '''Wrap an enum'''
    typename = enum.name
    values = ""
    for enumerator in enum.enumerators:
        values += "pub const " + str(enumerator.name)
        values += ": " + typename
        values += " = " + str(enumerator.value.value) + ";\n"
    return ENUM_TEMPLATE.format(name=typename, values=values[:-1])


def wrap_function(function):
    names = [arg.name for arg in function.args]
    types = [type_to_rust(arg.type) for arg in function.args]
    # Filter arguments named 'type'
    names = [n if n != "type" else "_type" for n in names]
    args = ", ".join(n + ": " + t for (n, t) in zip(names, types))

    ret = type_to_rust(function.rettype)
    if ret == "c_int":
        ret = "CHFL_STATUS"
    return FUNCTION_TEMPLATE.format(name=function.name, args=args, returns=ret)


def write_ffi(filename, ffi):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        fd.write(CRATES)
        for name in TYPES:
            fd.write(TYPE_TEMPLATE.format(name=name))

        for enum in ffi.enums:
            fd.write(wrap_enum(enum))

        fd.write(MANUAL_DEFS)
        fd.write(EXTERN_START)

        for function in ffi.functions:
            fd.write(wrap_function(function))

        fd.write(EXTERN_END)
