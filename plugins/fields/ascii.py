# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, length, reverse, info='', **kwargs):
    """Fixed-length ascii string."""

    def fget(self):
        buf = self.byteaccess.read_ascii(offset, length)
        return buf[::-1] if reverse else buf

    def fset(self, value):
        self.write_ascii(offset, length,
                         value[::-1] if reverse else value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)
