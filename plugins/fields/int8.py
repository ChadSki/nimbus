# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, info='', **kwargs):
    """8-bit (1-byte) signed integer."""

    def fget(self):
        return self.byteaccess.read_int8(offset)

    def fset(self, value):
        self.byteaccess.write_int8(offset, value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)
