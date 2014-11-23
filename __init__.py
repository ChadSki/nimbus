# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from byteaccess import FileContext, MemContext
from plugins import struct_type, set_fields_dir, set_plugins_dir
from halotag import HaloTag
import os
import re


class HaloMap(object):

    """TODO."""

    def __init__(self):
        self.context = None
        """TODO"""

        self.magic = None
        """TODO"""

        self.tags_by_ident = None
        """TODO"""

    def tags(self, first_class='', *name_fragments):
        """Search for tags by class and name fragments.

        Arguments:
        first_class -- All or part of the primary class name ('weap', 'bipd', ...)
                       Use the empty string to include all classes in your search.
                       Regular expressions are supported.

        *name_fragments -- All remaining arguments are independently searched for in tag
                           names, e.g. 'assault', 'rifle'. Only tags which contain all
                           fragments will be returned. Regular expressions are supported.
        """
        return filter(
            lambda tag: (first_class == '' or re.search(first_class, tag.first_class)
                         and all(regex == '' or re.search(regex, tag.name)
                                 for regex in name_fragments)),
            self.tags_by_ident.values())


def load_map(map_path=None):
    """Load a map from disk, or from Halo's memory if no filepath is specified.

    Arguments:
    map_path -- Location of the map on disk.
    """
    halomap = HaloMap()  # end result, assembled piece-by-piece

    if map_path is not None:
        location = 'file'
        halomap.context = FileContext(map_path)

    else:
        location = 'mem'
        halomap.context = MemContext('halo.exe')

    ByteAccess = halomap.context.ByteAccess

    if location == 'mem':
        # Force Halo to render video even when window is deselected
        exe_offset = 0x400000
        wmkillHandler_offset = exe_offset + 0x142538
        ByteAccess(wmkillHandler_offset, 4).WriteBytes(0, b'\xe9\x91\x00\x00')

    # fetch the necessary struct layouts
    MapHeader = struct_type('map_header')
    IndexHeader = struct_type('index_header')
    TagHeader = struct_type('tag_header')

    # load the map header
    map_header =\
        MapHeader(
            ByteAccess(offset={'file': 0, 'mem': 0x6A8154}[location],
                       size=MapHeader.struct_size),
            halomap)

    # load the index header
    index_header =\
        IndexHeader(
            ByteAccess(
                offset={'file': map_header.index_offset, 'mem': 0x40440000}[location],
                size=IndexHeader.struct_size),
            halomap)

    if location == 'file':
        # Usually the tag index directly follows the index header. However, some forms
        # of map protection move the tag index to other locations.
        index_offset = map_header.index_offset + index_header.primary_magic - 0x40440000

        # On disk, we need to use a magic value to convert raw pointers into file
        # offsets. This magic value is based on the tag index's location within the
        # file, since the tag index always appears at the same place in memory.
        halomap.magic = index_header.primary_magic - index_offset

    elif location == 'mem':
        # Almost always 0x40440028, unless the map has been protected in a specific way.
        index_offset = index_header.primary_magic

        # In memory, offsets are just raw pointers and require no adjustment.
        halomap.magic = 0

    # load all tag headers from the index
    tag_headers = [TagHeader(ByteAccess(offset=TagHeader.struct_size * i + index_offset,
                                        size=TagHeader.struct_size),
                             halomap) for i in range(index_header.tag_count)]

    # metadata can have pointers to unknown places, but at least we know where to start
    meta_offsets = sorted(tag_header.meta_offset_raw for tag_header in tag_headers)

    if location == 'file':  # the BSP's meta has an offset of 0, skip it
        bsp_offset = meta_offsets.pop(0)

    elif location == 'mem':  # the BSP's meta has a very large, distant offset, skip it
        bsp_offset = meta_offsets.pop()

    # to calculate sizes, we need the offset to the end of the metadata region (does
    # not point to a tag)
    meta_offsets.append(meta_offsets[0] + map_header.metadata_size)

    # [0, 10, 40, 60] from location offsets...
    #  [10, 30, 20]   we can calculate sizes...
    meta_sizes = {  # but instead of an ordered list, key based on the start offset
        start: (end - start) for start, end in zip(meta_offsets[:-1], meta_offsets[1:])
    }

    # just give the BSP's meta a size of zero for now
    meta_sizes.update({bsp_offset: 0})

    # not sure what the actual limit is; just picking some value
    name_maxlen = 256

    # build associative tag collection (ID => HaloTag)
    halomap.tags_by_ident = {
        tag_header.ident:
            HaloTag(tag_header,
                    ByteAccess(offset=tag_header.name_offset_raw - halomap.magic,
                               size=name_maxlen),
                    ByteAccess(offset=tag_header.meta_offset_raw - halomap.magic,
                               size=meta_sizes[tag_header.meta_offset_raw]),
                    halomap) for tag_header in tag_headers
    }

    return halomap

if __name__ == '__main__':
    halolib = os.path.join(os.environ['DROPBOX'],
                           r'Workbench\CodeProjects\HaloFiles\Source Code\Halolib')
    set_fields_dir(os.path.join(halolib, r'plugins\fields'))
    set_plugins_dir(os.path.join(halolib, r'converter\output'))
    m = load_map('./beavercreek.map')

    for tag in m.tags():
        print(repr(tag))
