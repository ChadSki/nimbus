# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, length, reverse, info, **kwargs):
    """Fixed-length ascii string."""

    def fget(self):
        answer = self.byteaccess.read_ascii(offset, length)
        if reverse:
            answer = answer[::-1]
        return answer

    def fset(self, value):
        if reverse:
            value = value[::-1]
        self.byteaccess.write_ascii(offset, value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)
