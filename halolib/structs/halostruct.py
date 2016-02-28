# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from basicstruct import BasicStruct

class HaloStruct(BasicStruct):

    """TODO"""

    def __init__(self, byteaccess, *, halomap, **kwargs):
        self.halomap = halomap
        super().__init__(byteaccess, **kwargs)

def define_halo_struct(**fields):
    def finish_construction(byteaccess):
        return BasicStruct(byteaccess, **fields)
    return finish_construction
