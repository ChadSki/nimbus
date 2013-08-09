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

from xmlplugins import load_plugin
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
        answer = str(self.map_header) + '\n\n'
        answer += str(self.index_header) + '\n\n'
        answer += 'Tag classes in order:\n'
        curr_column = 0

        for each in self.tags_in_order:
            answer += str(each.name) + '\n'

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
        pass

    @meta.setter
    def meta(self, value):
        pass

    def __getattr__(self, name):
        return getattr(self.index_entry, name)


def load_map_from_file(map_path):
    MapHeader = load_plugin('map_header.xml')
    IndexHeader = load_plugin('index_header.xml')
    IndexEntry = load_plugin('index_entry.xml')

    f = open(map_path, 'r+b')
    mapfile = mmap.mmap(f.fileno(), 0)

    mh = MapHeader(FileAccess(mapfile, 0, MapHeader.struct_size))
    ih = IndexHeader(FileAccess(mapfile, mh.index_offset, IndexHeader.struct_size))

    # In a standard map, ih.primary_magic and standard_magic are the same. However, Halo also
    # accepts non-standard tag index locations, which the following can handle: (thanks Zero2!)
    standard_magic = 0x40440028
    index_location = mh.index_offset + IndexHeader.struct_size + (ih.primary_magic - standard_magic)
    map_magic = ih.primary_magic - index_location

    index_entries = []
    curr_offset = index_location
    for i in range(ih.tag_count):
        ie = IndexEntry(FileAccess(mapfile, curr_offset, IndexEntry.struct_size))
        name_access = FileAccess(mapfile, ie.name_offset_raw - map_magic, 256)
        meta_access = FileAccess(mapfile, ie.meta_offset_raw - map_magic, 16)

        ht = HaloTag(ie, name_access, meta_access)

        print(ht.first_class)

        index_entries.append(ht)

        curr_offset += IndexEntry.struct_size


    #tn = TagName(FileAccess(mapfile, ie.name_offset_raw + map_magic, name_length))
    #md = Metadata(FileAccess(mapfile, ie.meta_offset_raw + map_magic, meta_size))
    #tags_in_order.append(HaloTag(ie, tn, md))

    hm = HaloMap(mh, ih, index_entries, f)
    print(hm)
    hm.close()
    
load_map_from_file('beavercreek.map')