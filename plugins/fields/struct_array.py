# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, struct_class, info='', **kwargs):
    """A pointer to an array of structs."""

    def fget(self):
        count = self.byteaccess.read_uint32(offset)
        raw_offset = self.byteaccess.read_uint32(offset + 4)

        start_offset = raw_offset - self.halomap.magic
        size = struct_class.struct_size

        if count > 1024:  # something's fucky
            raise RuntimeError('{} structs in struct_array?!'.format(count))

        return [struct_class(self.halomap.context.ByteAccess(
                                start_offset + i * size, size),
                             self.halomap)
                for i in range(count)]

    def fset(self, value):
        raise NotImplementedError(
            'Assigning entire struct arrays is not yet supported.')

    return NotifyProperty(name=name, fget=fget, fset=fset, doc=info)
