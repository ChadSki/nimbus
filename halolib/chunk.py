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

import glob
import os
import xml.etree.ElementTree as et
from halolib.field import make_field_property


chunk_classes = {}

class Chunk(object):
    """A base class for Halo structs which contains primitive and composite
    fields, and 0 or more references to other chunks. Chunk layouts are
    defined in XML."""

    def __init__(self, access, map_magic, halomap):
        self.access = access
        self.map_magic = map_magic
        self.halomap = halomap

    def __str__(self):

        def chunk_to_s(struct, answer='', indent='\n    '):
            """Recursively stringifies the base struct as well as reflexives"""
            for field_name in struct.field_names:
                value = getattr(struct, field_name)
                if type(value) == list:
                    for i, reflexive_chunk in enumerate(value):
                        answer += indent + field_name + '[%d]:' % i
                        answer = chunk_to_s(reflexive_chunk, answer, indent + '    ')
                else:
                    answer += indent + field_name + ': ' + str(value)

            return answer

        return chunk_to_s(self) + '\n'

def load_plugin(layout):
    """Using an xml-defined layout, define a new Python class which wraps a c-struct"""

    # define a subclass of Chunk using the name from xml
    new_class = type(layout.attrib['name'], (Chunk,), {})

    def __init__(self, *args, **kwargs):

        self.field_names = []
        for node in layout:
            if 'name' in node.attrib:
                self.field_names.append(node.attrib['name'])

        super(new_class, self).__init__(*args, **kwargs)

    new_class.__init__ = __init__
    new_class.struct_size = int(layout.attrib['struct_size'], base=0)

    for node in layout:
        child_chunk_class = None
        if node.tag == 'reflexive':
            child_chunk_class = load_plugin(node)

        setattr(new_class, node.attrib['name'], make_field_property(node, child_chunk_class))

    # save entire plugins for later
    if layout.tag == 'plugin':
        chunk_classes[layout.attrib['name']] = new_class

    # reflexives are used immediately to help construct plugins
    else:
        return new_class

def load_plugins():
    """Load all xml plugins from the plugin directory"""

    plugin_list = glob.glob(os.path.join('.\plugins', '*.xml'))
    for filepath in plugin_list:
        root_struct = et.parse(filepath).getroot()  # load the xml definition
        load_plugin(root_struct)
