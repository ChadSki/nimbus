# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .structs import tag_types, add_offsets

class HaloTag(object):

    """Represents one Halo tag and all of its data.

    Attributes
    ----------
    header : ObservableStruct
        Exposes fields from the TagHeader struct in the tag index.

    data : ObservableStruct
        Exposes fields from the tag's data structs.
    """

    def __init__(self, header, halomap):
        self.halomap = halomap
        self.header = header
        try:
            meta_offset = add_offsets(self.halomap.magic_offset,
                lambda magic: header.meta_offset_raw - magic)

            self.data = tag_types[header.first_class](
                halomap, meta_offset)
        except KeyError:
            self.data = None

    def __str__(self):
        """Returns a 1-line string representation of this tag."""
        answer = '[{}]{}({})'.format(self.first_class, self.name, self.ident)
        return repr(answer).replace("'", '"')

    def __repr__(self):
        """Returns a full string representation of this tag."""
        return '{}: {}'.format(str(self), str(self.data))

    def __getattr__(self, name):
        """Look for attributes in the following order:
            1. self
            2. self.header
            3. self.data
        """
        try:
            return getattr(self.header, name)
        except:
            return getattr(self.data, name)
