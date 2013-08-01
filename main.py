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
#     * Neither the name of the organization nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
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
from byteaccess import FileAccess
import mmap

class HaloMap(object):
    def __init__(self, map_header, index_header, tags_in_order):
        self.map_header = map_header
        self.index_header = index_header
        self.tags_in_order = tags_in_order

    def __str__(self):
        answer = str(self.map_header) + '\n\n'
        answer += str(self.index_header) + '\n\n'
        answer += 'Tag classes in order:\n'
        curr_column = 0
        for each in self.tags_in_order:
            answer += str(each.first_class) + ' '
            curr_column += 1
            if curr_column == 256:
                curr_column = 0
                answer += '\n'
        return answer

def load_map_from_file(map_path):
    MapHeader = load_plugin('map_header.xml')
    IndexHeader = load_plugin('index_header.xml')
    IndexEntry = load_plugin('index_entry.xml')

    f = open(map_path, 'r+b')
    mapfile = mmap.mmap(f.fileno(), 0)

    mh = MapHeader(FileAccess(mapfile, 0, MapHeader.struct_size))
    ih = IndexHeader(FileAccess(mapfile, mh.index_offset, IndexHeader.struct_size))
    #map_magic = 
    tags_in_order = []
    curr_offset = mh.index_offset + IndexHeader.struct_size
    for i in range(ih.tag_count):
        ie = IndexEntry(FileAccess(mapfile, curr_offset, IndexEntry.struct_size))
        #tn = TagName(FileAccess(mapfile, ie.))
        tags_in_order.append(ie)
        curr_offset += IndexEntry.struct_size

    hm = HaloMap(mh, ih, tags_in_order)
    print(hm)
    
load_map_from_file('beavercreek.map')