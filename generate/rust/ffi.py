# -* coding: utf-8 -*

"""
This module generate the Rust interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from generate.rust.constants import BEGINING
from generate.rust.convert import type_to_rust
from generate import CHFL_TYPES

MANUAL_DEFS = """
// Manual definitions. Edit the bindgen code to make sure this matches the
// chemfiles.h header
pub type c_bool = u8;
pub type chfl_vector_t = [c_double; 3];
pub type chfl_warning_callback = extern fn(*const c_char);

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct chfl_match_t {
    pub size: uint64_t,
    pub atoms: [uint64_t; 4],
}
// End manual definitions

"""

TYPE_TEMPLATE = "pub enum {name}{{}}\n"

ENUM_TEMPLATE = """
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum {name} {{
{values}
}}
"""

FUNCTION_TEMPLATE = """    pub fn {name}({args}) -> {returns};\n"""

EXTERN_START = """
#[link(name="chemfiles", kind="static")]
extern "C" {
"""

EXTERN_END = "}\n"

CRATES = """
#![allow(non_camel_case_types)]
extern crate libc;
use libc::{c_double, c_char, uint64_t, int64_t};
"""


def wrap_enum(enum):
    '''Wrap an enum'''
    typename = enum.name
    values = ""
    for enumerator in enum.enumerators:
        values += "    " + str(enumerator.name) + " = "
        values += str(enumerator.value.value) + ",\n"
    return ENUM_TEMPLATE.format(name=typename, values=values[:-1])


def wrap_function(function):
    names = [arg.name for arg in function.args]
    types = [type_to_rust(arg.type) for arg in function.args]
    # Filter arguments named 'type'
    names = [n if n != "type" else "_type" for n in names]
    args = ", ".join(n + ": " + t for (n, t) in zip(names, types))

    ret = type_to_rust(function.rettype)
    if ret == "c_int":
        ret = "chfl_status"
    return FUNCTION_TEMPLATE.format(name=function.name, args=args, returns=ret)


def write_ffi(filename, ffi):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        fd.write(CRATES)

        fd.write(MANUAL_DEFS)

        for name in CHFL_TYPES:
            fd.write(TYPE_TEMPLATE.format(name=name))

        for enum in ffi.enums:
            fd.write(wrap_enum(enum))

        fd.write(EXTERN_START)

        for function in ffi.functions:
            fd.write(wrap_function(function))

        fd.write(EXTERN_END)
