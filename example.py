# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from __future__ import print_function

import os
import sys
src_dir = os.path.dirname(__file__)
stdlib_location = os.path.abspath(src_dir + r"..\MetroIde\Lib")
dlls_location = os.path.abspath(src_dir + r"..\bin\Debug")
halolib_location = os.path.abspath(src_dir)
sys.path.append(stdlib_location)
sys.path.append(r"C:\Dropbox\Workbench\CodeProjects\HaloFiles\Source Code\Quickbeam\src\bin\Debug")
sys.path.append(halolib_location)

import clr
clr.AddReference("Quickbeam.Low.dll")

import halolib

curr_tag = halolib.load_map()
print(repr(curr_tag))

curr_tag.triggers[0].projectiles_per_shot /= 2
