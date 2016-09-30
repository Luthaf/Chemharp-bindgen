# -* coding: utf-8 -*

"""
This module generate the Python interface declaration for the functions it
finds in a C header. It only handle edge cases for the chemfiles.h header.
"""
import os
from .constants import BEGINING
from .convert import type_to_java

BEGINING += """
package chemfiles.lib;

import com.sun.jna.*;
import com.sun.jna.ptr.*;
"""

LIB_IMPORTS = """
import chemfiles.lib.Match;
import chemfiles.lib.LoggingCallback;
"""

LIBRARY = """
public class Lib {
    static {
        Native.register("chemfiles");
    }
"""

FUNCTION_TEMPLATE = "    public native static {restype} {name}({args});\n"

CHFL_LOGGING_CALLBACK = """
public interface LoggingCallback extends Callback {
    void log(int level, byte[] message);
}
"""

CHFL_MATCH_T = """
import java.util.Arrays;
import java.util.List;

public class Match extends Structure {
    public long size;
    public long[] atoms = new long[4];

    @Override
    protected List<String> getFieldOrder() {
        return Arrays.asList("size", "atoms");
    }
}
"""


def interface(function):
    '''Convert a function interface to Ctypes'''
    args = [
        type_to_java(arg.type, cdef=True) + " " + arg.name
        for arg in function.args
    ]
    args = ", ".join(args)
    restype = type_to_java(function.rettype)

    return FUNCTION_TEMPLATE.format(name=function.name,
                                    args=args,
                                    restype=restype)


def write_types(root):
    with open(os.path.join(root, "Match.java"), "w") as fd:
        fd.write(BEGINING)
        fd.write(CHFL_MATCH_T)

    with open(os.path.join(root, "LoggingCallback.java"), "w") as fd:
        fd.write(BEGINING)
        fd.write(CHFL_LOGGING_CALLBACK)


def write_functions(filename, functions):
    with open(filename, "w") as fd:
        fd.write(BEGINING)
        fd.write(LIB_IMPORTS)

        fd.write(LIBRARY)

        for func in functions:
            fd.write(interface(func))
        fd.write("}\n")
