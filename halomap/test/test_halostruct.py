# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import unittest
import halomap

class BloodGulchTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_importing(self):
        import halomap
        from halomap.halomapfield import StructArray, TagReference
        assert True


if __name__ == '__main__':
    unittest.main()
