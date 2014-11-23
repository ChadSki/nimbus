# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, bit, info, **kwargs):
    """A boolean flag."""

    def fget(self):
        return self.byteaccess.read_bit(offset, bit)

    def fset(self, value):
        return self.byteaccess.write_bit(offset, bit, value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)
