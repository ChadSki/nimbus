# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import os
import unittest
from halolib import HaloMap

def find_maps_folder():
    for drive in ('C:\\', 'D:\\', 'E:\\'):  # probably enough drives
        for arch in ('Program Files (x86)', 'Program Files'):
            maps_folder = os.path.join(drive, arch, 'Microsoft Games', 'Halo', 'MAPS')
            if os.path.exists(maps_folder):
                return maps_folder
    raise FileNotFoundError('Cannot find Halo MAPS folder.')


class BloodGulchTest(unittest.TestCase):

    def setUp(self):
        bloodgulch_path = os.path.join(find_maps_folder(), 'bloodgulch.map')
        self.map = HaloMap.from_file(bloodgulch_path)

    def test_importing(self):
        assert True


if __name__ == '__main__':
    unittest.main()
