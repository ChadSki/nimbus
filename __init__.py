# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .halomap import HaloMap

__all__ = ['HaloMap']

print("""Welcome to Halolib!
Try `m = halolib.HaloMap.from_memory()`
or  `m = halolib.HaloMap.from_file('infinity.map')`
and play with `m`. """)
