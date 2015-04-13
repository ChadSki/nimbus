# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .plugins import struct_type


class HaloTag(object):

    """Encapsulates an index entry, tag name, and metadata."""

    def __init__(self, tag_header, name_access, meta_access, halomap):
        # these attributes are all protected from erroneous assignment
        self.tag_header = tag_header
        self.name_access = name_access
        self.meta_access = meta_access
        self.halomap = halomap
        self._meta = None

    @property
    def name(self):
        return self.name_access.read_asciiz(0, maxlength=256)

    @name.setter
    def name(self, value):
        raise NotImplementedError('Changing tag names not yet implemented.')

    @property
    def meta(self):
        if self._meta is None:
            tag_type = struct_type(self.tag_header.first_class)
            self._meta = tag_type(self.meta_access, self.halomap)
        return self._meta

    @meta.setter
    def meta(self, value):
        raise NotImplementedError('Replacing the entire meta at once is not supported.')

    def __str__(self):
        """Returns a 1-line string representation of this tag."""
        answer = '[{}]{}({})'.format(self.tag_header.first_class,
                                     self.name,
                                     self.tag_header.ident)
        return repr(answer).replace("'", '"')

    def __repr__(self):
        """Returns a full string representation of this tag and its metadata."""
        return '{}: {}'.format(str(self), str(self.meta))
