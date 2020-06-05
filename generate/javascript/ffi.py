# -* coding: utf-8 -*

"""
This module generate the Typescript interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
from .constants import BEGINING
from .convert import return_type_to_js, arg_type_to_js
from generate import CHFL_TYPES

MANUAL_DEFINITIONS = """
// === Manual type declarations
declare const tag: unique symbol;
type POINTER = number & { readonly [tag]: 'pointer' };

export type CHFL_PTR = POINTER & { readonly [tag]: 'chemfile pointer' };
type c_char_ptr = POINTER & { readonly [tag]: 'char pointer' };
type c_char_ptr_ptr = POINTER & { readonly [tag]: 'char array pointer' };
type c_bool_ptr = POINTER & { readonly [tag]: 'bool pointer' };
type c_double_ptr = POINTER & { readonly [tag]: 'double pointer' };
type c_uint64_ptr = POINTER & { readonly [tag]: 'uint64_t pointer' };
type chfl_bond_order_ptr = POINTER & { readonly [tag]: 'chfl_bond_order pointer' };
type chfl_property_kind_ptr = POINTER & { readonly [tag]: 'chfl_property_kind pointer' };
type chfl_cellshape_ptr = POINTER & { readonly [tag]: 'chfl_cellshape pointer' };
type function_ptr = POINTER & { readonly [tag]: 'function pointer' };

type c_char = number;
type c_bool = number;
type c_double = number;

type chfl_bond_order = number;
type chfl_property_kind = number;
type chfl_cellshape = number;
type chfl_status = number;

type chfl_vector3d = c_double_ptr;
type chfl_match_ptr = POINTER;

// === Manual functions declarations
type LLVMType = 'i8' | 'i16' | 'i32' | 'i64' | 'float' | 'double' | '*';
export declare function getValue(ptr: POINTER, type: LLVMType): number;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export declare function setValue(ptr: POINTER, value: any, type: LLVMType): void;
export declare function UTF8ToString(ptr: c_char_ptr, maxBytesToRead?: number): string;
export declare function stringToUTF8(str: string, ptr: c_char_ptr, maxBytesToWrite: number): void;

export declare function stackSave(): number;
export declare function stackAlloc(size: number): POINTER;
export declare function stackRestore(saved: number): void;

// eslint-disable-next-line @typescript-eslint/ban-types
export declare function addFunction(fn: Function, signature: string): function_ptr;

export declare function _malloc(size: number): POINTER;
export declare function _free(ptr: POINTER): void;

export declare function then(callback: () => void): void;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export declare const FS: any;

export declare const HEAP8: Int8Array;
export declare const HEAP16: Int16Array;
export declare const HEAP32: Int32Array;
export declare const HEAPU8: Uint8Array;
export declare const HEAPU16: Uint16Array;
export declare const HEAPU32: Uint32Array;
export declare const HEAPF32: Float32Array;
export declare const HEAPF64: Float64Array;
// === End of manual declarations

"""

TYPE_TEMPLATE = "export type {name} = CHFL_PTR & {{ readonly [tag]: '{name}' }};\n"

ENUM_TEMPLATE = """
export enum {name} {{
{values}
}}
"""

FUNCTION_TEMPLATE = """
// '{name}' at {coord}
export declare function _{name}({args}): {restype};
"""

EXTRA_EXPORTED_RUNTIME_METHODS = [
    "stringToUTF8",
    "UTF8ToString",
    "getValue",
    "setValue",
    "stackSave",
    "stackAlloc",
    "stackRestore",
    "addFunction",
    "FS",
]


def write_declarations(filename, functions):
    with open(filename, "w") as fd:
        fd.write(BEGINING)

        for name in EXTRA_EXPORTED_RUNTIME_METHODS:
            assert name in MANUAL_DEFINITIONS
        fd.write(MANUAL_DEFINITIONS)

        for name in CHFL_TYPES:
            fd.write(TYPE_TEMPLATE.format(name=name))

        for function in functions:
            fd.write(interface(function))


def write_main(filename, enums):
    with open(filename, "w") as fd:
        fd.write(BEGINING)

        fd.write("export * from './cdecl';\n")

        for enum in enums:
            typename = enum.name
            values = ""
            for enumerator in enum.enumerators:
                values += "    " + str(enumerator.name) + " = "
                values += str(enumerator.value.value) + ",\n"
            fd.write(ENUM_TEMPLATE.format(name=typename, values=values[:-1]))


def write_cmake_export(path, functions):
    with open(path, "w") as fd:
        fd.write("set(EXPORTED_FUNCTIONS\n\"")
        fd.write(", ".join(["'_{}'".format(f.name) for f in functions]))
        fd.write("\"\n)\n")

        fd.write("set(EXTRA_EXPORTED_RUNTIME_METHODS\n\"")
        fd.write(", ".join([
            "'{}'".format(name) for name in EXTRA_EXPORTED_RUNTIME_METHODS
        ]))
        fd.write("\"\n)\n")


def interface(function):
    names = []
    types = []
    for arg in function.args:
        if not arg.type.is_ptr and arg.type.cname == "uint64_t":
            # emscripten passes uint64_t as two uint32_t, for high and low bits
            # when working with chemfiles, we can (usually) ignore the high
            # bits, since uint64_t are used to store size_t values only, which
            # will be 32-bits on WASM (for now, while only wasm32 exists)
            names.append(arg.name + "_lo")
            names.append(arg.name + "_hi")
            types.append('number')
            types.append('number')
        else:
            names.append(arg.name)
            types.append(arg_type_to_js(arg.type))

    args = ", ".join(n + ": " + t for (n, t) in zip(names, types))

    restype = return_type_to_js(function.rettype)

    return FUNCTION_TEMPLATE.format(
        name=function.name,
        coord=function.coord,
        args=args,
        restype=restype,
    )
