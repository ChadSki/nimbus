# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, length, info='', **kwargs):
    """Just bytes."""

    def fget(self):
        return self.byteaccess.ReadBytes(offset, length)

    def fset(self, value):
        self.byteaccess.WriteBytes(offset, value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)
