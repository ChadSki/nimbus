# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

"""
from .structs import struct_type


class HaloTag(object):

    "'"Represents one Halo tag and all of its data.

    Attributes
    ----------
    header : ObservableStruct
        todo

    data : ObservableStruct
        todo
    "'"

    def __init__(self, offsets, halomap):
        self.halomap = halomap
        self.header = struct_type('tag_header')(offsets, halomap)
        self.data = struct_type(header.first_class)(
            offset=header.meta_offset_raw,
            halomap=halomap)

    def __str__(self):
        "'"Returns a 1-line string representation of this tag.
        "'"
        answer = '[{}]{}({})'.format(self.first_class, self.name, self.ident)
        return repr(answer).replace("'", '"')

    def __repr__(self):
        "'"Returns a full string representation of this tag and its metadata.
        "'"
        return '{}: {}'.format(str(self), str(self.data))

    def __getattr__(self, name):
        "'"Using dynamic magic, merge the attributes of self.data into this object.

        Attributes resolve in the following order:
            1. self
            2. self.data
        "'"
        return getattr(self.data, name)
"""

import basicstruct

class HaloMapStruct(BasicStruct):
    pass

