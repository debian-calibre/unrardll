#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: BSD Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import os
import unicodedata
import unittest
from binascii import crc32

from unrardll import (
    BadPassword, PasswordRequired, comment, extract, extract_member, headers, names,
    open_archive, unrar
)

from . import TempDir, TestCase, base

multipart_rar = os.path.join(base, 'example_split_archive.part1.rar')
password_rar = os.path.join(base, 'example_password_protected.rar')
simple_rar = os.path.join(base, 'simple.rar')
sr_data = {
    '1': b'',
    '1/sub-one': b'sub-one\n',
    '2': b'',
    '2/sub-two.txt': b'sub-two\n',
    'Füße.txt': b'unicode\n',
    'max-compressed': b'max\n',
    'one.txt': b'one\n',
    'symlink': b'sub-two',
    'uncompressed': b'uncompressed\n',
    '诶比屁.txt': b'chinese unicode\n'}


def normalize(x):
    return unicodedata.normalize('NFC', x)


def get_memory():
    'Return memory usage in bytes'
    # See https://pythonhosted.org/psutil/#psutil.Process.memory_info
    try:
        import psutil
    except ImportError:
        raise unittest.SkipTest('psutil is not available')
    return psutil.Process(os.getpid()).memory_info().rss


def memory(since=0.0):
    'Return memory used in MB. The value of since is subtracted from the used memory'
    ans = get_memory()
    ans /= float(1024**2)
    return ans - since


class BasicTests(TestCase):

    def test_names(self):
        all_names = [
            '1/sub-one', 'one.txt', '诶比屁.txt', 'Füße.txt', '2/sub-two.txt',
            'symlink', '1', '2', 'uncompressed', 'max-compressed']
        self.ae(all_names, list(names(simple_rar)))
        all_names.remove('symlink'), all_names.remove('1'), all_names.remove('2')
        self.ae(all_names, list(names(simple_rar, only_useful=True)))

    def test_comment(self):
        self.ae(comment(simple_rar), 'some comment\n')
        self.ae(comment(password_rar), '')

    def test_share_open(self):
        with open(simple_rar, 'rb') as f:
            self.ae(comment(simple_rar), 'some comment\n')
            f.close()

    def test_extract(self):
        for v in (True, False):
            with TempDir() as tdir:
                extract(simple_rar, tdir, verify_data=v)
                h = {
                    normalize(os.path.abspath(os.path.join(tdir, h['filename']))): h
                    for h in headers(simple_rar)}
                data = {}
                for dirpath, dirnames, filenames in os.walk(tdir):
                    for f in filenames:
                        path = normalize(os.path.join(dirpath, f))
                        data[os.path.relpath(path, tdir).replace(os.sep, '/')] = d = open(path, 'rb').read()
                        if f == 'one.txt':
                            self.ae(os.path.getmtime(path), 1098472879)
                        self.ae(h[path]['unpack_size'], len(d))
                        self.ae(h[path]['file_crc'] & 0xffffffff, crc32(d) & 0xffffffff)
            q = {k: v for k, v in sr_data.items() if v}
            del q['symlink']
            self.ae(data, q)

    def test_password(self):
        with TempDir() as tdir:
            self.assertRaises(PasswordRequired, extract, password_rar, tdir)
            self.assertRaises(BadPassword, extract, password_rar, tdir, password='sfasgsfdg')
            extract(password_rar, tdir, password='example')

    def test_invalid_callback(self):
        class Callback(object):
            pass
        with open_archive(simple_rar, None, mode=unrar.RAR_OM_EXTRACT) as f:
            unrar.read_next_header(f)
            self.assertRaisesRegexp(unrar.UNRARError, "An exception occurred in the password callback handler", unrar.process_file, f)
        c = Callback()
        c._process_data = lambda x: None
        with open_archive(simple_rar, c, mode=unrar.RAR_OM_EXTRACT) as f:
            unrar.read_next_header(f)
            self.assertRaisesRegexp(unrar.UNRARError,  "Processing canceled by the callback", unrar.process_file, f)

    def test_multipart(self):
        self.ae(list(names(multipart_rar)), ['Fifteen_Feet_of_Time.pdf'])
        for v in (True, False):
            with TempDir() as tdir:
                extract(multipart_rar, tdir, verify_data=v)
                h = next(headers(multipart_rar))
                raw = open(os.path.join(tdir, h['filename']), 'rb').read()
                self.ae(len(raw), h['unpack_size'])
                self.ae(hashlib.sha1(raw).hexdigest(), 'a9fc6a11d000044f17fcdf65816348ce0be3b145')

    def test_extract_member(self):
        self.ae(extract_member(simple_rar, lambda h: h['filename'] == 'one.txt', verify_data=True), ('one.txt', sr_data['one.txt']))
        self.ae(extract_member(simple_rar, lambda h: False), (None, None))

    def test_open_failure(self):
        self.assertRaises(OSError, extract, 'sdfgsfgsggsdfg.rar', '.')

    def test_memory_leaks(self):
        import gc

        def collect():
            for i in range(6):
                gc.collect()
            gc.collect()

        with TempDir() as tdir:

            def get_mem_use(num):
                collect()
                start = memory()
                for i in range(num):
                    extract(simple_rar, tdir)
                collect()
                return max(0, memory(start))

            get_mem_use(5)  # ensure no memory used by get_mem_use itself is counted
            a, b = get_mem_use(10), get_mem_use(100)
        self.assertTrue(a == 0 or b/a < 3, '10 times usage: {} 100 times usage: {}'.format(a, b))
