# -* coding: utf-8 -*
"""
This module generate chemfiles Fortran API by calling the C interfae
"""
import os
import copy
from generate.functions import Argument, CHFL_TYPES
from generate.ctype import ArrayType, StringType, PtrToArrayType, CType

from .constants import BEGINING, FORTRAN_TYPES, STRING_LENGTH
from .convert import arg_to_fortran, function_name_to_fortran, CONVERSIONS

TEMPLATE = """
subroutine {name}({args})
    implicit none
{declarations}

{instructions}
end subroutine
"""

STR_FUNCTIONS = ["chfl_strerror", "chfl_last_error"]

TEMPLATE_STR_FUNCTIONS = """
function {name}({args}) result(string)
    implicit none
{declarations}
    character(len={str_len}) :: string
    type(c_ptr) :: c_string

    c_string = {cname}({args})
    string = c_to_f_str(c_string)
end function
"""

SET_OPTIONAL_TEMPLATE = """
    if (present({name})) then
        {name}_tmp_ = {name}
    else
        {name}_tmp_ = {default}
    end if
"""

COPY_OPTIONAL_TEMPLATE = """
    if (present({name})) then
        {name} = {name}_tmp_
    end if"""

CHECK_NULL_POINTER = """

    if (.not. c_associated(this%ptr)) then
        status_tmp_ = CHFL_MEMORY_ERROR
    else
        status_tmp_ = CHFL_SUCCESS
    end if
"""

SET_POINTER_TO_NULL = """    this%ptr = c_null_ptr"""


DEFAULT_VALUES = {
    "resid": "-1",
    "velocity": "[0.0, 0.0, 0.0]",
}


def call_interface(args):
    '''
    Translate the arguments from fortran to C in function call
    '''
    args_call = []
    for arg in args:
        name = arg.name

        if name == "status":
            continue

        if arg.type.is_optional:
            name += "_tmp_"

        if isinstance(arg.type, StringType) and arg.type.is_const:
            # Convert const string
            call = "f_to_c_str(" + name + ")"
        elif isinstance(arg.type, ArrayType):
            # Use pointers for arrays
            if isinstance(arg.type, PtrToArrayType):
                call = "c_loc(c_" + name + "_)"
            else:
                call = "c_loc(" + name + ")"
        else:
            call = name
            if str(arg.type) in CHFL_TYPES or name == "this":
                call += "%ptr"
        args_call.append(call)

    interface = "(" + ", ".join(args_call) + ")"
    return interface


def pre_call_processing(args):
    '''Pre-process arguments before call'''
    res = ""
    for arg in args:
        # Set default values as needed
        if arg.type.is_optional and arg.name != "status":
            default = DEFAULT_VALUES[arg.name]
            res += SET_OPTIONAL_TEMPLATE.format(name=arg.name, default=default)
    return res


def post_call_processing(args):
    '''Post-process arguments after call'''
    res = ""
    for arg in args:
        if isinstance(arg.type, StringType) and not arg.type.is_const:
            res += arg.name + " = rm_null_in_str(" + arg.name + ")"
        # Only the status needs to be passed back to the caller
        if arg.name == "status":
            assert arg.type.is_optional
            res += COPY_OPTIONAL_TEMPLATE.format(name=arg.name)
    return res


def cleanup_arguments(functions):
    for function in functions:
        # If the function is a constructor, prepend the "this" argument in the
        # arguments list
        if function.is_constructor:
            type_ = CType(
                cname=function.rettype.cname,
                ctype=function.rettype,
                is_ptr=True
            )
            function.args = [Argument("this", type_)] + function.args
            function.fname = function.name + "_init_"

        if not isinstance(function.rettype, StringType):
            chfl_status = CType(cname="chfl_status", ctype="chfl_status")
            chfl_status.is_optional = True
            function.args.append(Argument("status", chfl_status))

        # Replace the first argument name by "this" if it is one of the
        # chemfiles types.
        try:
            arg = function.args[0]
            typename = arg.type.cname
            if typename.startswith("CHFL_"):
                arg.name = "this"
        except IndexError:
            pass


def write_functions(path, functions):
    with open(path, "w") as fd:
        fd.write(BEGINING)
        for function in functions:
            declarations = "\n".join([arg_to_fortran(arg, interface=True)
                                     for arg in function.args])

            if isinstance(function.rettype, StringType):
                fd.write(TEMPLATE_STR_FUNCTIONS.format(
                    name=function.name,
                    cname="c_" + function.name,
                    args=function.args_str(),
                    declarations=declarations,
                    str_len=STRING_LENGTH))
            else:
                for arg in function.args:
                    if isinstance(arg.type, PtrToArrayType):
                        declarations += "\n    type(c_ptr), target :: "
                        declarations += "c_" + arg.name + "_"
                    if arg.type.is_optional:
                        declarations += "\n    " + CONVERSIONS[arg.type.cname]
                        declarations += " :: " + arg.name + "_tmp_"

                instructions = ""
                instructions += pre_call_processing(function.args)

                if function.is_constructor:
                    instructions += "    this%ptr = "
                    instructions += "c_" + function.name
                    instructions += call_interface(function.args[1:])
                    instructions += CHECK_NULL_POINTER
                else:
                    instructions += "    status_tmp_ = "
                    instructions += "c_" + function.name
                    instructions += call_interface(function.args)

                for arg in function.args:
                    if isinstance(arg.type, PtrToArrayType):
                        instructions += "\n    call c_f_pointer("
                        instructions += "c_" + arg.name + "_, " + arg.name
                        # Hard-coding the shape for now
                        instructions += ", shape=[3, int(size, c_int)])"

                post_call = post_call_processing(function.args)
                if post_call:
                    instructions += "\n    " + post_call

                if (function.name.endswith("_free") or
                   function.name == "chfl_trajectory_close"):
                        instructions += "\n" + SET_POINTER_TO_NULL

                fd.write(TEMPLATE.format(
                    name=function_name_to_fortran(function),
                    args=function.args_str(),
                    declarations=declarations,
                    instructions=instructions))


def write_wrappers(root, functions):
    '''
    Generate fortran subroutines corresponding to the C functions
    '''
    # Create a local copy of the functions list
    functions = copy.copy(functions)
    cleanup_arguments(functions)

    for type in FORTRAN_TYPES:
        write_functions(
            os.path.join(root, type + ".f90"),
            filter(lambda function: function.name.startswith(type), functions)
        )

    others = []
    for function in functions:
        name = "_".join(function.name.split("_")[:2])
        if (name not in FORTRAN_TYPES and
           function.name != "chfl_set_warning_callback"):
                others.append(function)

    write_functions(os.path.join(root, "others.f90"), others)
