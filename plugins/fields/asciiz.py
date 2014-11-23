# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*args, name, offset, maxlength, info, **kwargs):
    """Null-terminated ascii string."""

    def fget(self):
        return self.byteaccess.ReadAsciiz(offset, maxlength)

    def fset(self, value):
        self.byteaccess.WriteAsciiz(offset, value, maxlength)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)
