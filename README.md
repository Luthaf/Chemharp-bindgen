# Binding generator for [Chemharp](https://github.com/Luthaf/Chemharp)

This is a python module for parsing the `chemharp.h` header and generating the
corresponding FFI code for other bindings based on the C interface for Chemharp.

This code depend on the [pycparser](https://github.com/eliben/pycparser/) Python module.

Now, this code can generate the full Fortran binding, and the FFI for the Python binding.
