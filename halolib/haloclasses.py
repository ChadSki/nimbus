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

from halolib.xmlplugins import load_plugins, py_strlen, halo_struct_classes
from halolib.byteaccess import FileAccess, access_process
import mmap

class HaloMap(object):
    def init(self, map_header, index_header, tags, map_magic, file=None):
        self.map_header = map_header
        self.index_header = index_header
        self.tags = tags
        self.map_magic = map_magic
        self.file = file

        self.tags_by_id = {}
        for each in tags:
            self.tags_by_id[each.ident] = each

    def __str__(self):
        return '%s\n%s' % (str(self.map_header) % '', str(self.index_header) % '')

    def get_tag(self, first_class, name_fragment=''):
        for tag in self.tags:
            if tag.first_class == first_class and name_fragment in tag.name:
                return tag

        return None
    
    def get_tags(self, first_class, name_fragment=''):
        for tag in self.tags:
            if tag.first_class == first_class and name_fragment in tag.name:
                yield tag
    

    def close(self):
        if self.file != None:
            self.file.close()
            self.file = None


class HaloTag(object):
    def __init__(self, index_entry, name_access, meta_access, map_magic, halomap):
        object.__setattr__(self, 'index_entry', index_entry)
        object.__setattr__(self, 'name_access', name_access)
        object.__setattr__(self, 'meta_access', meta_access)
        object.__setattr__(self, 'map_magic', map_magic)
        object.__setattr__(self, 'halomap', halomap)

    def __str__(self):
        return '[%s]%s(%d)' % (self.first_class, self.name, self.ident)

    @property
    def layout(self):
        return str(self.meta) % self.name

    @property
    def name(self):
        name_bytes = self.name_access.read_all_bytes()
        name_length = py_strlen(name_bytes)
        return name_bytes[:name_length].decode('ascii')

    @name.setter
    def name(self, value):
        pass

    @property
    def meta(self):
        # every time the meta is accessed, reinterpret it as the current first_class
        return halo_struct_classes[self.first_class](self.meta_access, self.map_magic, self.halomap)

    # HaloTag (using magic) sort of merges the attributes of self.index_entry and self.meta alongside its own
    #
    # Getting an attribute resolves in the following order:
    #   1. First self's attributes are checked
    #   2. If nothing was found, Python will run __getattr__ and check self.index_entry's attributes
    #   3. If nothing was found in self.index_entry, check self.meta
    #   4. If checking self.meta fails just let the AttributeError propagate upwards

    def __getattr__(self, name):
        try:
            return getattr(self.index_entry, name)
        except AttributeError:
            return getattr(self.meta, name)

    # Setting an attribute resolves in the following order:
    #   1. index_entry, name_access, and meta_access are exempt from being replaced
    #   2. Other attributes of self can be assigned to
    #   3. If no such attribute is found in self, check self,index_entry
    #   3. If no such attribute is found in self.index_entry, check self.meta
    #   4. If checking self.meta fails, return without setting anything

    def __setattr__(self, name, value):
        if name in ['meta', 'index_entry', 'name_access', 'meta_access', 'map_magic', 'halomap']:
            pass

        elif name in self.__dict__:
            object.__setattr__(self, name, value)

        elif hasattr(self.index_entry, name):
            setattr(self.index_entry, name, value)

        elif hasattr(self.meta, name):
            setattr(self.meta, name, value)

        else:
            pass


def load_map_from_file(map_path):
    MapHeader = halo_struct_classes['map_header']
    IndexHeader = halo_struct_classes['index_header']
    IndexEntry = halo_struct_classes['index_entry']

    f = open(map_path, 'r+b')
    mmap_file = mmap.mmap(f.fileno(), 0)

    halomap = HaloMap()

    map_header = MapHeader(FileAccess(mmap_file, 0, MapHeader.struct_size), 0, halomap)
    index_header = IndexHeader(FileAccess(mmap_file, map_header.index_offset, IndexHeader.struct_size), 0, halomap)

    # Usually a map's primary magic is exactly equal to the 'standard primary magic'
    # defined here. However, some forms of map protection move the tag index to other
    # locations, which results in a different primary magic. (Thanks for explaining, Zero2!)
    standard_primary_magic = 0x40440028
    standard_index_location = map_header.index_offset + IndexHeader.struct_size
    primary_magic_difference = index_header.primary_magic - standard_primary_magic
    index_location = standard_index_location + primary_magic_difference

    # map magic is based on primary magic and the index location
    map_magic = index_header.primary_magic - index_location

    tags = []
    curr_offset = index_location
    for i in range(index_header.tag_count):
        index_entry = IndexEntry(FileAccess(mmap_file, curr_offset, IndexEntry.struct_size), map_magic, halomap)
        name_access = FileAccess(mmap_file, index_entry.name_offset_raw - map_magic, 256)
        meta_access = FileAccess(mmap_file, index_entry.meta_offset_raw - map_magic, 0x4000)

        ht = HaloTag(index_entry, name_access, meta_access, map_magic, halomap)
        tags.append(ht)

        curr_offset += IndexEntry.struct_size

    halomap.init(map_header, index_header, tags, map_magic, f)
    return halomap


def load_map_from_memory(*, fix_video_render=False):
    WinMemAccess = access_process('halo.exe')

    # Force Halo to render video even when window is deselected
    if fix_video_render:
        video_rendering = WinMemAccess(0x400000 + 0x142538, 16)
        video_rendering.write_bytes(b'\xe9\x91\x00\x00', 0)

    MapHeader = halo_struct_classes['map_header']
    IndexHeader = halo_struct_classes['index_header']
    IndexEntry = halo_struct_classes['index_entry']

    halomap = HaloMap()

    # Not sure where the map header lives in Halo 1.09's memory space...
    map_header = 'No MapHeader\n%s' #MapHeader(WinMemAccess(0xDEADBEEF, MapHeader.struct_size), 0, halomap)
    index_header = IndexHeader(WinMemAccess(0x40440000, IndexHeader.struct_size), 0, halomap)

    tags = []
    curr_offset = index_header.primary_magic

    for i in range(index_header.tag_count):
        index_entry = IndexEntry(WinMemAccess(curr_offset, IndexEntry.struct_size), 0, halomap)
        name_access = WinMemAccess(index_entry.name_offset_raw, 256)
        meta_access = WinMemAccess(index_entry.meta_offset_raw, 0x4000)

        ht = HaloTag(index_entry, name_access, meta_access, 0, halomap)
        tags.append(ht)

        curr_offset += IndexEntry.struct_size

    halomap.init(map_header, index_header, tags, 0)
    return halomap
