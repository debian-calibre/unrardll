#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: BSD Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import absolute_import, division, print_function, unicode_literals

import importlib
import os
import re
import sys
from distutils.command.build import build as Build

from setuptools import Extension, setup

self_path = os.path.abspath(__file__)
base = os.path.dirname(self_path)
iswindows = hasattr(sys, 'getwindowsversion')
raw = open(os.path.join(base, 'src/unrardll/__init__.py'),
           'rb').read().decode('utf-8')
version = map(
    int, re.search(r'^version = V\((\d+), (\d+), (\d+)', raw, flags=re.M).groups())


def include_dirs():
    ans = []
    if 'UNRAR_INCLUDE' in os.environ:
        ans.extend(os.environ['UNRAR_INCLUDE'].split(os.pathsep))
    return ans


def libraries():
    return ['unrar']


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


def find_tests():
    import unittest
    suites = []
    for f in os.listdir(os.path.join(base, 'test')):
        n, ext = os.path.splitext(f)
        if ext == '.py' and n not in ('__init__',):
            m = importlib.import_module('test.' + n)
            suite = unittest.defaultTestLoader.loadTestsFromModule(m)
            suites.append(suite)
    return unittest.TestSuite(suites)


class Test(Build):

    description = "run unit tests after in-place build"

    def run(self):
        import unittest
        Build.run(self)
        if self.dry_run:
            self.announce('skipping "test" (dry run)')
            return
        sys.path.insert(0, self.build_lib)
        tests = find_tests()
        r = unittest.TextTestRunner
        result = r(verbosity=2).run(tests)

        if not result.wasSuccessful():
            raise SystemExit(1)


CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Archiving :: Compression
"""

setup(
    name=str('unrardll'),
    version='{}.{}.{}'.format(*version),
    author='Kovid Goyal',
    author_email='redacted@acme.com',
    description='Wrap the Unrar DLL to enable unraring of files in python',
    license='BSD',
    url='https://github.com/kovidgoyal/unrardll',
    classifiers=[c for c in CLASSIFIERS.split("\n") if c],
    platforms=['any'],
    packages=[str('unrardll')],
    package_dir={'': str('src')},
    cmdclass={'test': Test},
    ext_modules=[
        Extension(
            str('unrardll.unrar'),
            include_dirs=include_dirs(),
            libraries=libraries(),
            library_dirs=library_dirs(),
            define_macros=macros(),
            sources=[str('src/unrardll/wrapper.cpp')]
        )
    ]
)
