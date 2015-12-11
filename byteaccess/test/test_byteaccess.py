# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import unittest
import byteaccess

def string_tests(context, offset):
    """Test some string functions of ByteAccess with overlapping access regions"""
    foo = context.ByteAccess(offset, 21)
    bar = context.ByteAccess(offset, 4)

    assert foo.read_bytes(0, 4) == b'asdf'
    assert foo.read_bytes(4, 10) == b'0123456789'
    foo.write_bytes(0, b'test')
    assert foo.read_bytes(0, 4) == b'test'
    assert bar.read_all_bytes() == foo.read_bytes(0, 4)
    bar.write_bytes(0, b'asdf')
    assert foo.read_bytes(0, 4) == b'asdf'

def number_tests(context, offset):
    """Test some number functions of ByteAccess with overlapping access regions"""
    foo = context.ByteAccess(offset, 21)
    baz = context.ByteAccess(offset + 15, 16)

    foo.write_float32(0, 2.0)
    foo.write_float64(4, 15.3)
    assert foo.read_float32(0) == 2.0
    assert foo.read_float64(4) == 15.3

    foo.write_int8(0, 12)
    foo.write_int16(1, 13)
    foo.write_int32(3, 14)
    foo.write_int64(7, 14)
    assert foo.read_int8(0) == 12
    assert foo.read_int16(1) == 13
    assert foo.read_int32(3) == 14
    assert foo.read_int64(7) == 14


class MyTest(unittest.TestCase):

    def test_filebyteaccess(self):
        import os
        this_folder = os.path.dirname(os.path.realpath(__file__))
        context = byteaccess.FileContext(os.path.join(this_folder, 'testfile.bin'))
        string_tests(context, 0)
        number_tests(context, 0)


    def test_membyteaccess(self):
        context = byteaccess.MemContext('halo')

        # ensure we can read the map header
        foo = context.ByteAccess(0x6A8154, 4)
        assert foo.read_all_bytes() == b'daeh'
        foo.write_bytes(0, b'toof')
        assert foo.read_all_bytes() == b'toof'
        foo.write_bytes(0, b'daeh')
        assert foo.read_all_bytes() == b'daeh'


if __name__ == '__main__':
    unittest.main()
