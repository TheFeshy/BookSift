#!/usr/bin/env python

"""
setup.py uses the python distutils to create compile the c++ code into a python module.
"""

from distutils.core import setup, Extension


my_module = Extension('_OptimizeCompare',
                           sources=['OptimizeCompare.i', 'OptimizeCompare.cpp'],
                           swig_opts=['-c++'] #TODO: try with -builtin for speed!
                           )

setup (name = 'BookSiftOptimize',
       version = '0.1',
       author      = "Dave",
       description = """Optimized LCS (or TCS) search""",
       ext_modules = [my_module],
       #py_modules = ["OptimizeCompare"],
       url="https://github.com/TheFeshy/BookSift"
       )