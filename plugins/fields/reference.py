# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import NotifyProperty


def field(*, name, offset, loneid='False', info, **kwargs):

    if loneid not in ('True', 'False'):
        raise ValueError(
            'LoneID attribute set to "{}", must be "True" or "False".'.format(loneid))

    # LoneIDs (idents just by themselves) need no adjustment.
    if loneid != 'True':
        # This is a full reference, and we only care to read the ident
        offset += 12  # (which is located 12 bytes inside)

    def fget(self):
        ident = self.byteaccess.ReadUInt32(offset)
        if ident == 0 or ident == 0xFFFFFFFF:
            return None
        else:
            return self.halomap.tags_by_ident[ident]  # the referenced tag

    def fset(self, value):
        # when value is None, write Halo's version of null (-1)
        # otherwise, write the tag's ident, not the tag itself
        self.byteaccess.WriteUInt32(offset,
                                    0xFFFFFFFF if value is None
                                    else value.ident)

    return NotifyProperty(name=name, fget=fget, fset=fset, doc=info)
