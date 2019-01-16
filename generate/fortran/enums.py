# -* coding: utf-8 -*
"""
This module generate the a Fortran declaration for the C enums.
"""
from .constants import BEGINING

TEMPLATE = """
enum, bind(C)
    {enumerators}
end enum

integer, parameter :: {name} = kind({first_enumerator})
"""


def enum_to_fortran(enum):
    names_values = [
        "enumerator :: " + e.name + " = " + e.value.value
        for e in enum.enumerators
    ]

    return "\n    ".join(names_values)


def write_enums(path, enums):
    '''
    Generate the enum wrapping to Fortran
    '''
    with open(path, "w") as fd:
        fd.write(BEGINING)
        for enum in enums:
            fd.write(TEMPLATE.format(
                enumerators=enum_to_fortran(enum),
                name=enum.name,
                first_enumerator=enum.enumerators[0].name
            ))
