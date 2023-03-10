#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: BSD Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import absolute_import, division, print_function, unicode_literals

import importlib
import os
import sys

from setuptools import Command, Extension, setup

iswindows = hasattr(sys, 'getwindowsversion')


def find_tests():
    import unittest
    suites = []
    for f in os.listdir('test'):
        n, ext = os.path.splitext(f)
        if ext == '.py' and n not in ('__init__',):
            m = importlib.import_module('test.' + n)
            suite = unittest.defaultTestLoader.loadTestsFromModule(m)
            suites.append(suite)
    return unittest.TestSuite(suites)


class Test(Command):

    description = "run unit tests after in-place build"
    user_options = []
    sub_commands = [
        ('build', None),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import unittest
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
        build = self.get_finalized_command('build')
        sys.path.insert(0, os.path.abspath(build.build_lib))
        if iswindows and 'UNRAR_DLL_DIR' in os.environ and hasattr(os, 'add_dll_directory'):
            unrardir = os.path.join(build.build_lib, 'unrardll')
            sys.save_dll_dir = os.add_dll_directory(os.environ['UNRAR_DLL_DIR'])
            print('Added Dll directory:', sys.save_dll_dir,
                  'with contents:', os.listdir(os.environ['UNRAR_DLL_DIR']))
            print('Contents of build dir:', unrardir, os.listdir(unrardir), flush=True)
        tests = find_tests()
        r = unittest.TextTestRunner
        result = r(verbosity=2).run(tests)

        if not result.wasSuccessful():
            raise SystemExit(1)


def include_dirs():
    ans = []
    if 'UNRAR_INCLUDE' in os.environ:
        ans.extend(os.environ['UNRAR_INCLUDE'].split(os.pathsep))
    return ans


def library_dirs():
    ans = []
    if 'UNRAR_LIBDIRS' in os.environ:
        ans.extend(os.environ['UNRAR_LIBDIRS'].split(os.pathsep))
    return ans


def macros():
    ans = [
        ('SILENT', 1),
        ('RARDLL', 1),
        ('UNRAR', 1), ]
    if not iswindows:
        ans.append(('_UNIX', 1))
    return ans


setup(
    cmdclass={'test': Test},
    ext_modules=[
        Extension(
            str('unrardll.unrar'),
            include_dirs=include_dirs(),
            libraries=['unrar'],
            library_dirs=library_dirs(),
            define_macros=macros(),
            sources=[str('src/unrardll/wrapper.cpp')]
        )
    ]
)
