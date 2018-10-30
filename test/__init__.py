#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: BSD Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import sys
import tempfile
import unittest

base = os.path.dirname(os.path.abspath(__file__))
iswindows = hasattr(sys, 'getwindowsversion')


class TestCase(unittest.TestCase):

    ae = unittest.TestCase.assertEqual
    longMessage = True
    tb_locals = True
    maxDiff = None


class TempDir(object):

    def __enter__(self):
        self.tdir = tempfile.mkdtemp()
        if isinstance(self.tdir, bytes):
            self.tdir = self.tdir.decode(sys.getfilesystemencoding())
        return self.tdir

    def __exit__(self, *a):
        shutil.rmtree(self.tdir)
        del self.tdir
