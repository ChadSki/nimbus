# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, info, **kwargs):
    """16-bit (2-byte) unsigned integer."""

    def fget(self):
        return self.byteaccess.read_uint16(offset)

    def fset(self, value):
        self.byteaccess.write_uint16(offset, value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)