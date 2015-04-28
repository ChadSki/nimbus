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
    tag_header : ObservableStruct
        todo

    tag_data : ObservableStruct
        todo

    name : string
        property ? todo ???
    """

    def __init__(self, header, halomap):
        self.halomap = halomap
        self.header = header
        self.data = struct_type(self.tag_header.first_class)(
            offset=self.tag_header.meta_offset_raw,
            halomap=self.halomap)

        self.name_access = self.halomap.context.ByteAccess(
            offset=self.header.name_offset_raw,
            size=256)

    @property
    def name(self):
        return self.name_access.read_asciiz(0, maxlength=256)

    @name.setter
    def name(self, value):
        raise NotImplementedError('Changing tag names not yet implemented.')

    def __str__(self):
        """Returns a 1-line string representation of this tag."""
        answer = '[{}]{}({})'.format(self.header.first_class,
                                     self.name,
                                     self.tag_header.ident)
        return repr(answer).replace("'", '"')

    def __repr__(self):
        """Returns a full string representation of this tag and its metadata."""
        return '{}: {}'.format(str(self), str(self.tag_data))
