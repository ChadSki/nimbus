# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import re
from .byteaccess import FileContext, MemContext
from .plugins import struct_type
from .halotag import HaloTag


class HaloMap(object):

    """Halo map object.

    Attributes
    ----------
    tags_by_ident : Dict[int, HaloTag]
        All tags in this map, accessible by unique id.

    context
        Data context from which the map was loaded.
    """

    @staticmethod
    def from_memory(mirror_path=None):
        """Load a map from Halo's memory. Changes immediately take effect in-game,
        but will be lost unless saved to disk.

        Parameters
        ----------
        mirror_path : string, optional
            Location of the map on disk to open for mirroring changes. If None,
            changes made in memory are not saved and will be lost.
        """
        if mirror_path is not None:
            raise NotImplementedError()

        return HaloMap(MemContext('halo.exe'))

    @staticmethod
    def from_file(map_path):
        """Load a map from a local mapfile. Changes immediately take effect;
        keep backups of your map files!

        Parameters
        ----------
        map_path : string
            Location of the map on disk to open for editing.
        """
        return HaloMap(FileContext(map_path))

# if location == 'mem':
#     # Force Halo to render video even when window is deselected
#     # exe_offset = 0x400000
#     wmkillHandler_offset = 0x542018  # exe_offset + 0x142538
#     self.context.RawByteAccess(wmkillHandler_offset, 4)\
#         .write_bytes(0, b'\xe9\x91\x00\x00')

    def __init__(self, context):
        """Load a map from the given context (either a file or Halo's memory).

        Parameters
        ----------
        context
            Data context from which to read map data.
        """
        self.context = context

        MapHeader = struct_type('map_header')
        self.map_header = MapHeader(offsets={'file': 0, 'mem': 0x6A8154},
                                    halomap=self)

        IndexHeader = struct_type('index_header')
        self.index_header = IndexHeader(offsets={'file': self.map_header.index_offset,
                                                 'mem': 0x40440000},
                                        halomap=self)

        # Almost always 0x40440028, unless the map has been protected in
        # a specific way.
        mem_index_offset = self.index_header.primary_magic

        # Usually the tag index directly follows the index header. However,
        # some forms of map protection move the tag index to other locations.
        file_index_offset = (self.index_header.primary_magic - 0x40440000
                             + self.map_header.index_offset)

        # On disk, we need to use a magic value to convert raw pointers into file
        # offsets. If this is a disk or mirror context, it will automatically make
        # use of this magic number. Memory contexts will ignore it, since offsets
        # in memory are already pointers.
        self.context.magic = self.index_header.primary_magic - file_index_offset

        TagHeader = struct_type('tag_header')
        tag_headers = [
            TagHeader(
                offsets={'file': TagHeader.struct_size * i + file_index_offset,
                         'mem': TagHeader.struct_size * i + mem_index_offset},
                halomap=self)
            for i in range(self.index_header.tag_count)]

        # build associative tag collection (ID => HaloTag)
        self.tags_by_ident = {
            tag_header.ident: HaloTag(header=tag_header,
                                      halomap=self)
            for tag_header in tag_headers}

    def tag(self, tag_class='', *name_fragments):
        """Find a tag by name and class. Returns the first tag to match all
        criteria, or None.

        Parameters
        ----------
        tag_class : string
            Filter your search by a full or partial tag class name. Use the
            empty string to include all classes in your search. Regular
            expressions are enabled.

            Examples: '', 'bipd', 'obje', 'proj|weap|vehi', 's(cex|chi|gla)'

        name_fragments : tuple of string, optional
            Each fragment is independently searched for in tag names. Only tags
            which contain all fragments will be returned. Regular expressions
            are enabled.

            Example fragments: '', 'cyborg', 'rifle|pistol'
        """
        return next(self.tags(tag_class, name_fragments), None)

    def tags(self, tag_class='', *name_fragments):
        """Filter tags by name and class.

        Parameters
        ----------
        tag_class : string
            Filter your search by a full or partial tag class name. Use the
            empty string to include all classes in your search. Regular
            expressions are enabled.

            Examples: '', 'bipd', 'obje', 'proj|weap|vehi', 's(cex|chi|gla)'

        name_fragments : tuple of string, optional
            Each fragment is independently searched for in tag names. Only tags
            which contain all fragments will be returned. Regular expressions
            are enabled.

            Example fragments: '', 'cyborg', 'rifle|pistol'
        """
        def match(tag):
            return (any(re.search(tag_class, tag.tag_header.first_class),
                        re.search(tag_class, tag.tag_header.second_class),
                        re.search(tag_class, tag.tag_header.second_class))

                    and all(regex == '' or re.search(regex, tag.name)
                            for regex in name_fragments))

        return filter(match, self.tags_by_ident.values())

    def save_as(filepath):
        raise NotImplementedError()
