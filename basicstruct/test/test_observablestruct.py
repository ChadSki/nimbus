# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import unittest
import basicstruct

class BasicStructTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_importing(self):
        from basicstruct.struct import Event, BasicStruct
        from basicstruct.field import Field
        from basicstruct.field import (
            Ascii, Asciiz, AsciizPtr, RawData,
            Enum16, Flag, Float32, Float64,
            Int8, Int16, Int32, Int64,
            UInt8, UInt16, UInt32, UInt64)
        assert True

if __name__ == '__main__':
    unittest.main()
