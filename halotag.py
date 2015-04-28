# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .plugins import struct_type


class HaloTag(object):

    """Represents one Halo tag and all of its data.

    Attributes
    ----------
    header : ObservableStruct
        todo

    data : ObservableStruct
        todo
    """

    def __init__(self, header, halomap):
        self.halomap = halomap
        self.header = header
        self.data = struct_type(header.first_class)(
            offset=header.meta_offset_raw,
            halomap=halomap)

    def __str__(self):
        """Returns a 1-line string representation of this tag."""
        answer = '[{}]{}({})'.format(self.first_class,
                                     self.name,
                                     self.ident)
        return repr(answer).replace("'", '"')

    def __repr__(self):
        """Returns a full string representation of this tag and its metadata."""
        return '{}: {}'.format(str(self), str(self.data))
