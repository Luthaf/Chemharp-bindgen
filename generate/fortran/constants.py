# -* coding: utf-8 -*
"""
Various constants for fortran API generation
"""

# Maximum string length
STRING_LENGTH = 1024

# List of type which have to be wrapped to fortran
FORTRAN_TYPES = [
    "chfl_trajectory", "chfl_cell", "chfl_atom", "chfl_frame", "chfl_topology",
    "chfl_selection", "chfl_residue", "chfl_property",
]

LICENCE = """! Chemfiles, an efficient IO library for chemistry file formats
! Copyright (C) 2015-2017 Guillaume Fraux -- BSD licence
"""

BEGINING = LICENCE + """!
! =========================================================================== !
! !!!! AUTO-GENERATED FILE !!!! Do not edit. See bindgen repository for the
! generating code (https://github.com/chemfiles/bindgen).
! This file contains Fortran 2003 ISO C Binding interface to the C API
!
! This file is not compilable on his own, but should be 'include'd in another
! fortran compilation unit.
! =========================================================================== !

"""
