# Copyright (c) 2015, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from field import Field


class HaloField(Field):

    """Fields that require a halomap to make sense, and can count on their
    parent struct to retain a reference to one."""

    @property
    def halomap(self):
        return self.parent.halomap


class TagReference(HaloField):

    """Semantic link to a HaloTag."""

    def __init__(self, *, loneid='False', **kwargs):
        super().__init__(**kwargs)

        if loneid not in ('True', 'False'):
            raise ValueError(
                'LoneID attribute set to "{}",' +
                'must be "True" or "False".'.format(loneid))

        # LoneIDs (idents just by themselves) need no adjustment.
        if loneid != 'True':
            # This is a full reference, but we only care to read the ident
            self.offset += 12  # which is located 12 bytes inside

    def getf(self):
        ident = self.byteaccess.read_uint32(self.offset)
        if ident == 0 or ident == 0xFFFFFFFF:
            return None
        try:
            return self.halomap.tags_by_ident[ident]  # the referenced tag
        except KeyError:
            return None  # we wanted a tag that wasn't there =(

    def setf(self, value):
        # when value is None, write Halo's version of null (-1)
        # otherwise, write the tag's ident, not the tag itself
        self.byteaccess.write_uint32(self.offset,
                                     0xFFFFFFFF if value is None
                                     else value.ident)


class StructArray(HaloField):

    """A pointer to an array of structs."""

    def __init__(self, *, struct_type, halomap, **kwargs):
        super().__init__(**kwargs)
        self.struct_type = struct_type
        self.halomap = halomap

    def getf(self):
        count = self.byteaccess.read_uint32(self.offset)
        raw_offset = self.byteaccess.read_uint32(self.offset + 4)

        start_offset = raw_offset - self.halomap.magic
        size = self.struct_type.size

        if count > 1024:  # something's fucky
            raise RuntimeError('{} structs in struct_array?!'.format(count))

        return [self.struct_type(
                    self.halomap.context.ByteAccess(
                        start_offset + i * size, size))
                for i in range(count)]

    def setf(self, value):
        raise NotImplementedError(
            'Reassigning entire struct arrays is not yet supported.')
