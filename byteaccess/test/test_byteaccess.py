# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import os
import sys
sys.path.insert(0, os.path.abspath('..\..'))

import byteaccess


def string_tests(foo, bar, offset):
    assert foo.read_bytes(0, 4) == b'asdf'
    assert foo.read_bytes(4, 10) == b'0123456789'
    foo.write_bytes(0, b'test')
    assert foo.read_bytes(0, 4) == b'test'
    assert bar.read_all_bytes() == foo.read_bytes(0, 4)
    bar.write_bytes(0, b'asdf')
    assert foo.read_bytes(0, 4) == b'asdf'


def number_tests(foo, offset):
    foo.write_float32(offset + 0, 2.0)
    foo.write_float64(offset + 4, 15.3)
    assert foo.read_float32(offset + 0) == 2.0
    assert foo.read_float64(offset + 4) == 15.3

    foo.write_int8(offset + 0, 12)
    foo.write_int16(offset + 1, 13)
    foo.write_int32(offset + 3, 14)
    foo.write_int64(offset + 7, 14)
    assert foo.read_int8(offset + 0) == 12
    assert foo.read_int16(offset + 1) == 13
    assert foo.read_int32(offset + 3) == 14
    assert foo.read_int64(offset + 7) == 14


def test_filebyteaccess():
    context = byteaccess.FileContext('./testfile.bin')

    foo = context.ByteAccess(0, 21)
    bar = context.ByteAccess(0, 4)
    string_tests(foo, bar, 0)

    baz = context.ByteAccess(15, 16)
    number_tests(baz, 0)


def test_membyteaccess():
    context = byteaccess.MemContext('halo')
    foo = context.ByteAccess(0x6A8154, 4)
    assert foo.read_all_bytes() == b'daeh'
    foo.write_bytes(0, b'toof')
    assert foo.read_all_bytes() == b'toof'
    foo.write_bytes(0, b'daeh')
    assert foo.read_all_bytes() == b'daeh'


if __name__ == '__main__':
    test_filebyteaccess()
    print("File tests successful!")

    try:
        test_membyteaccess()
        print("Memory tests successful!")
    except RuntimeError:
        print("Aborting memory tests.")
