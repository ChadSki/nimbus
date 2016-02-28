# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import re
from byteaccess import FileContext, MemoryContext
from halostruct.structs.tags import tag_types


class HaloTag(object):

    """Represents one Halo tag and all of its data.

    Attributes
    ----------
    header : ObservableStruct
        todo

    data : ObservableStruct
        todo
    """

    def __init__(self, offsets, halomap):
        self.halomap = halomap
        self.header = struct_type('tag_header')(offsets, halomap)
        self.data = struct_type(header.first_class)(
            offset=header.meta_offset_raw,
            halomap=halomap)

    def __str__(self):
        """Returns a 1-line string representation of this tag.
        """
        answer = '[{}]{}({})'.format(self.first_class, self.name, self.ident)
        return repr(answer).replace("'", '"')

    def __repr__(self):
        """Returns a full string representation of this tag and its metadata.
        """
        return '{}: {}'.format(str(self), str(self.data))

    def __getattr__(self, name):
        """Using dynamic magic, merge the attributes of self.data into this object.

        Attributes resolve in the following order:
            1. self
            2. self.data
        """
        return getattr(self.data, name)


class HaloMap(object):

    """Represents a single Halo mapfile and everything in it.

    Attributes
    ----------
    map_header : HaloStruct
        todo

    index_header : HaloStruct
        todo

    tags_by_ident : Dict[int, HaloTag]
        Each tag in the map, addressable by unique id.

    context
        Data context from which the map was loaded. As a HaloMap object is edited,
        changes are written back via this context.
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
            raise NotImplementedError('Cannot mirror to disk yet.')

        return HaloMap(MemoryContext('halo.exe'))

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

    def __init__(self, context):
        """Load a map from the given context (either a file or Halo's memory).

        Parameters
        ----------
        context
            Where to read map data and write changes.
        """
        self.context = context

        self.map_header = struct_type('map_header')(
            offsets={'file': 0, 'mem': 0x6A8154},
            halomap=self)

        try:
            self.index_header = struct_type('index_header')(
                offsets={'file': self.map_header.index_offset, 'mem': 0x40440000},
                halomap=self)
        except AttributeError:
            print('************************************************************')
            print(self.map_header.store)
            print('***********************************************************2')
            raise

        # Almost always 0x40440028 (map protection may change this)
        mem_index_offset = self.index_header.primary_magic

        # Usually the tag index directly follows the index header. However,
        # some forms of map protection move the tag index to other locations.
        file_index_offset = (self.index_header.primary_magic - 0x40440000
                             + self.map_header.index_offset)

        # On disk, we need to use a magic value to convert raw pointers into file
        # offsets. If this is a disk context, it will use this magic number
        # automatically. Memory contexts will ignore it, since offsets in memory
        # are already valid pointers.
        self.context.magic = self.index_header.primary_magic - file_index_offset

        # build associative tag collection (ID => HaloTag)
        self.tags_by_ident = {
            tag_header.ident: HaloTag(
                offsets={'file': TagHeader.struct_size * i + file_index_offset,
                         'mem': TagHeader.struct_size * i + mem_index_offset},
                halomap=self)
            for i in range(self.index_header.tag_count)}

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
            Each fragment is independently searched for in tag names. Only a tag
            which contains all fragments will be returned. Regular expressions
            are enabled.

            Example fragments: '', 'cyborg', 'plasma.*(rifle|pistol)'
        """
        return next(self.tags(tag_class, name_fragments), None)

    def tags(self, tag_class='', *name_fragments):
        """Filter tags by name and class. Same as self.tag(), but iterates
        through all tags which match the search criteria.
        """
        def match(tag):
            return (any(re.search(tag_class, tag.first_class),
                        re.search(tag_class, tag.second_class),
                        re.search(tag_class, tag.third_class))

                    and all(re.search(regex, tag.name)
                            for regex in name_fragments))

        return filter(match, self.tags_by_ident.values())

    def save_as(filepath):
        raise NotImplementedError()
