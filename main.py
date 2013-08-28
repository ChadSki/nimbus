# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from xmlplugins import load_plugins
from xmlplugins import plugin_dict
from xmlplugins import py_strlen
from byteaccess import FileAccess
import mmap

class HaloMap(object):
    def __init__(self, map_header, index_header, tags_in_order, file=None):
        self.map_header = map_header
        self.index_header = index_header
        self.tags_in_order = tags_in_order
        self.file = file

    def __str__(self):
        answer = '%s\n\n' % str(self.map_header)
        answer += '%s\n\n' % str(self.index_header)

        answer += 'Tag classes in order:\n'
        column = 0
        for each in self.tags_in_order:
            answer += '%s ' % each.first_class
            column += 1
            if column > 50:
                answer += '\n'
                column = 0

        return answer

    def close(self):
        if self.file != None:
            self.file.close()
            self.file = None


class HaloTag(object):
    def __init__(self, index_entry, name_access, meta_access):
        self.index_entry = index_entry
        self.name_access = name_access
        self.meta_access = meta_access

    @property
    def name(self):
        name_bytes = self.name_access.read_all_bytes()
        name_length = py_strlen(name_bytes)
        return name_bytes[:name_length]

    @name.setter
    def name(self, value):
        pass

    @property
    def meta(self):
        # every time the meta is accessed, reinterpret it as the current class
        return plugin_dict[self.first_class](self.meta_access)

    @meta.setter
    def meta(self, value):
        pass

    def __getattr__(self, name):
        return getattr(self.index_entry, name)


def load_map_from_file(map_path):
    load_plugins('.')

    MapHeader = plugin_dict['map_header']
    IndexHeader = plugin_dict['index_header']
    IndexEntry = plugin_dict['index_entry']

    f = open(map_path, 'r+b')
    mmap_file = mmap.mmap(f.fileno(), 0)

    map_header = MapHeader(FileAccess(mmap_file, 0, MapHeader.struct_size))
    index_header = IndexHeader(FileAccess(mmap_file, map_header.index_offset, IndexHeader.struct_size))

    # Usually a map's primary magic is exactly equal to the 'standard primary magic'
    # defined here. However, some forms of map protection move the tag index to other
    # locations, which results in a different primary magic. (Thanks for explaining, Zero2!)
    standard_primary_magic = 0x40440028
    standard_index_location = map_header.index_offset + IndexHeader.struct_size
    primary_magic_difference = index_header.primary_magic - standard_primary_magic
    index_location = standard_index_location + primary_magic_difference

    # map magic is based on primary magic and the index location
    map_magic = index_header.primary_magic - index_location

    index_entries = []
    curr_offset = index_location

    for i in range(index_header.tag_count):
        index_entry = IndexEntry(FileAccess(mmap_file, curr_offset, IndexEntry.struct_size))
        name_access = FileAccess(mmap_file, index_entry.name_offset_raw - map_magic, 256)
        meta_access = FileAccess(mmap_file, index_entry.meta_offset_raw - map_magic, 16)

        ht = HaloTag(index_entry, name_access, meta_access)
        index_entries.append(ht)

        curr_offset += IndexEntry.struct_size


    #tn = TagName(FileAccess(mmap_file, index_entry.name_offset_raw + map_magic, name_length))
    #md = Metadata(FileAccess(mmap_file, index_entry.meta_offset_raw + map_magic, meta_size))
    #tags_in_order.append(HaloTag(index_entry, tn, md))

    hm = HaloMap(map_header, index_header, index_entries, f)
    print(hm)
    hm.close()
    
load_map_from_file('beavercreek.map')