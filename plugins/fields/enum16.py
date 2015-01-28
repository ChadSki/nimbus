# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, options, info='', **kwargs):
    """8-bit enumeration of options."""

    forward_options = {
        int(number): name for name, number in options.items()
    }  # type: Dict[int, str]

    reversed_options = {
        name: int(number) for name, number in options.items()
    }  # type: Dict[str, int]

    def fget(self):
        return forward_options[self.byteaccess.read_uint16(offset)]

    def fset(self, value):
        self.byteaccess.write_uint16(offset, reversed_options[value])

    doc = info + ('\n'.join('{} => {}'.format(number, name)
                            for name, number in options.items()))
    print(doc)  # TODO does this look right?

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=doc)
