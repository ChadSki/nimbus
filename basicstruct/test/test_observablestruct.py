# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import unittest
import byteaccess
import basicstruct
from basicstruct.struct import Event, basic_struct_factory
from basicstruct.field import Field
from basicstruct.field import (
    Ascii, Asciiz, AsciizPtr, RawData,
    Enum16, Flag, Float32, Float64,
    Int8, Int16, Int32, Int64,
    UInt8, UInt16, UInt32, UInt64)

class BasicStructTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_defining(self):
        ExeStruct = basic_struct_factory(
            exe_header=Ascii(offset=0, length=2, docs="named for some dude"))
        NotepadAccess = byteaccess.open_file(r"C:\Users\Chad\Downloads\ccsetup512.exe")
        foo = NotepadAccess(0, 2)
        bar = ExeStruct(foo)
        assert bar.exe_header == 'MZ'



if __name__ == '__main__':
    unittest.main()
