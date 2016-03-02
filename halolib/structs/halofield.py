# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import basicstruct
from basicstruct.field import BasicField


class HaloField(BasicField):

    """Fields that require a halomap to make sense, and can count on their
    parent struct to retain a reference to one."""

    @property
    def halomap(self):
        return self.parent.halomap


class AsciizPtr(HaloField):

    """Pointer to a null-terminated string somewhere else in the mapfile."""

    max_str_size = 260  # good ol' Windows MAX_PATH

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.string_access = None

    def getf(self, byteaccess):
        if self.string_access is None:
            name_offset = byteaccess.read_uint32(self.offset)
            self.string_access = self.halomap.map_access(
                name_offset - self.halomap.magic_offset,
                AsciizPtr.max_str_size)
        return self.string_access.read_asciiz(0, AsciizPtr.max_str_size)

    def setf(self, byteaccess):
        raise NotImplementedError()


class TagReference(HaloField):

    """Semantic link to a HaloTag."""

    def __init__(self, *, loneid=False, **kwargs):
        super().__init__(**kwargs)

        # LoneIDs (idents just by themselves) need no adjustment.
        if not loneid:
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

    """A pointer to an array of Halo structs somewhere else in the mapfile."""

    def __init__(self, *, struct_type, halomap, **kwargs):
        super().__init__(**kwargs)
        self.struct_type = struct_type
        self.halomap = halomap
        self.children = None

    def getf(self):
        if self.children is None:
            count = self.byteaccess.read_uint32(self.offset)
            raw_offset = self.byteaccess.read_uint32(self.offset + 4)

            start_offset = raw_offset - self.halomap.magic
            size = self.struct_type.size

            if count > 1024:  # something's fucky
                raise RuntimeError('{} structs in struct_array?!'.format(count))

            self.children = [self.struct_type(
                self.halomap.context.ByteAccess(
                    start_offset + i * size, size))
                for i in range(count)]
        return self.children

    def setf(self, value):
        raise NotImplementedError(
            'Reassigning entire struct arrays is not yet supported.')
