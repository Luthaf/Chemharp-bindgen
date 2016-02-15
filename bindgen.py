#!/usr/bin/env python3
# -* coding: utf-8 -*
import os
import sys
from generate import FFI
from generate import fortran
from generate import python


def usage():
    print("Usage: {} chemfiles.h python|fortran out/path".format(sys.argv[0]))


def parse_args(args):
    config = {}
    config["header"] = args[1]
    config["binding"] = args[2]
    config["outpath"] = args[3]

    config["cxx_includes"] = os.path.join(
        os.path.dirname(config["header"]),
        "..",
        "..",
        "include"
    )
    return config


def generate_fortran(config):
    ffi = FFI(
        [config["header"]],
        includes=[config["cxx_includes"]],
        defines=[("CHFL_EXPORT", "")]
    )

    root = config["outpath"]
    fortran.write_enums(os.path.join(root, "cenums.f90"), ffi.enums)
    ffi.functions = [f for f in ffi.functions if f.name != "chfl_log_callback"]
    fortran.write_cdef(os.path.join(root, "cdef.f90"), ffi.functions)

    fortran.write_types(os.path.join(root, "ftypes.f90"), ffi.functions)
    fortran.write_interface(
        os.path.join(root, "interface.f90"),
        ffi.functions
    )


def generate_python(config):
    ffi = FFI(
        [config["header"]],
        includes=[config["cxx_includes"]],
        defines=[("CHFL_EXPORT", "")]
    )

    root = config["outpath"]
    python.write_ffi(os.path.join(root, "ffi.py"), ffi.enums, ffi.functions)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage()
        sys.exit(1)
    config = parse_args(sys.argv)
    config["cxx_includes"] = os.path.dirname(config["header"])

    if config["binding"] == "fortran":
        generate_fortran(config)
    elif config["binding"] == "python":
        generate_python(config)
    else:
        usage()
        print("Unkown binding type: {}".format(config["binding"]))
        sys.exit(2)
