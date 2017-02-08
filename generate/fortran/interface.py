# -* coding: utf-8 -*
"""
This module generate chemfiles Fortran API by calling the C interfae
"""
import os
import copy
from generate.functions import Argument, CHFL_TYPES
from generate.ctype import ArrayType, StringType, PtrToArrayType, CType

from .constants import BEGINING, FORTRAN_TYPES, STRING_LENGTH
from .convert import arg_to_fortran, function_name_to_fortran

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

COPY_RETURN_STATUS = """
    if (present(status)) then
        status = status_tmp_
    end if"""

CHECK_NULL_POINTER = """

    if (.not. c_associated(this%ptr)) then
        status_tmp_ = CHFL_MEMORY_ERROR
    else
        status_tmp_ = CHFL_SUCCESS
    end if
"""


def call_interface(args):
    '''
    Translate the arguments from fortran to C in function call
    '''
    args_call = []
    for arg in args:
        if isinstance(arg.type, StringType) and arg.type.is_const:
            # Convert const string
            call = "f_to_c_str(" + arg.name + ")"
        elif isinstance(arg.type, ArrayType):
            # Use pointers for arrays
            if isinstance(arg.type, PtrToArrayType):
                call = "c_loc(c_" + arg.name + "_)"
            else:
                call = "c_loc(" + arg.name + ")"
        else:
            call = arg.name
            if str(arg.type) in CHFL_TYPES or arg.name == "this":
                call += "%ptr"
        args_call.append(call)

    interface = "(" + ", ".join(args_call) + ")"
    return interface


def post_call_processing(args):
    '''
    Post-process strings after call when needed
    '''
    res = ""
    for arg in args:
        if isinstance(arg.type, StringType) and not arg.type.is_const:
            res = arg.name + " = rm_null_in_str(" + arg.name + ")"
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
            new_arg = Argument("this", type_)
            function.args = [new_arg] + function.args
            function.fname = function.name + "_init_"

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
                declarations += "\n    integer(kind=chfl_status), optional :: status"
                declarations += "\n    integer(kind=chfl_status) :: status_tmp_"
                for arg in function.ptr_to_array_args():
                    declarations += "\n    type(c_ptr), target :: "
                    declarations += "c_" + arg.name + "_"

                instructions = ""
                args = ", ".join([arg.name for arg in function.args])

                if function.is_constructor:
                    instructions = "    this%ptr = "
                    instructions += "c_" + function.name
                    instructions += call_interface(function.args[1:])
                    instructions += CHECK_NULL_POINTER
                else:
                    instructions = "    status_tmp_ = "
                    instructions += "c_" + function.name
                    instructions += call_interface(function.args)

                for arg in function.ptr_to_array_args():
                    instructions += "\n    call c_f_pointer("
                    instructions += "c_" + arg.name + "_, " + arg.name
                    # Hard-coding the shape for now
                    instructions += ", shape=[3, int(size, c_int)])"
                instructions += COPY_RETURN_STATUS

                args += ", status" if args else "status"

                post_call = post_call_processing(function.args)
                if post_call:
                    instructions += "\n    " + post_call

                fd.write(TEMPLATE.format(
                    name=function_name_to_fortran(function),
                    args=args,
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
