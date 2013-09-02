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
from halolib.field import *

def make_property(node):
    """Defines a property which reads/writes to a field in a plugin-defined struct"""

    # to make a property we need three things:
    #  1) a getter function
    #  2) a setter function
    #  3) a docstring (optional)

    offset = int(node.attrib['offset'], base=0)

    if node.tag == 'reflexive':
        # handles the reflexive's count and pointer
        field = ReflexiveField(**node.attrib)

        # handles interpreting that which is pointed to
        Reflexive = load_plugin(node)

        def fget(self):
            buf = self.access.read_bytes(offset, 8)     # retrieve the struct as bytes
            count, raw_offset = field.get_value(buf)    # reinterpret the raw data

            structs = []
            curr_p = raw_offset - self.map_magic
            for i in range(count):
                structs.append(Reflexive(self.access.create_subaccess(curr_p, Reflexive.struct_size), self.map_magic, self.halomap))
                curr_p += Reflexive.struct_size

            return structs

        def fset(self, value):
            raise Exception("Writing an entire reflexive at once is not implemented")

    elif node.tag == 'reference':
        field = UInt32Field(**node.attrib)
        offset = int(node.attrib['offset'], base=0) + 12

        def fget(self):
            buf = self.access.read_bytes(offset, 4)     # retrieve the struct as bytes
            ident = field.get_value(buf)                # reinterpret the raw data with the selected reader

            if ident == 0 or ident == 0xFFFFFFFF:
                return None
            else:
                return self.halomap.tags_by_id[ident]   # return the referenced tag

        def fset(self, value):
            if value:
                ident = value.ident                     # write back the tag's ident, not the tag itself
            else:
                ident = 0xFFFFFFFF                      # Halo's version of null

            buf = self.access.read_bytes(offset, 4)     # retrieve the struct as bytes
            field.set_value(buf, ident)                 # write the new value by using the selected writer
            self.access.write_bytes(buf, offset)        # don't forget to write the bytes back!

    else: # primitives
        field_ctor, size_of = {
            'float' : (FloatField, 4),
            'double' : (DoubleField, 8),
            'int8' : (Int8Field, 1),
            'int16' : (Int16Field, 2),
            'int32' : (Int32Field, 4),
            'int64' : (Int64Field, 8),
            'uint8' : (UInt8Field, 1),
            'uint16' : (UInt16Field, 2),
            'uint32' : (UInt32Field, 4),
            'uint64' : (UInt64Field, 8),
            'rawdata' : (RawDataField, int(node.attrib.get('length', '0'), base=0)),
            'ascii' : (AsciiField, int(node.attrib.get('length', '0'), base=0)),
            'asciiz' : (AsciizField, int(node.attrib.get('maxlength', '0'), base=0)),
        }[node.tag]

        field = field_ctor(**node.attrib)

        def fget(self):
            buf = self.access.read_bytes(offset, size_of)   # retrieve the struct as bytes
            return field.get_value(buf)                     # reinterpret the raw data with the selected reader

        def fset(self, value):
            buf = self.access.read_bytes(offset, size_of)   # retrieve the struct as bytes
            field.set_value(buf, value)                     # write the new value by using the selected writer
            self.access.write_bytes(buf, offset)            # don't forget to write the bytes back!

    if 'description' in node.attrib:
        doc = node.attrib['description']
    else:
        doc = node.attrib['name'].replace('_', ' ')

    return property(fget=fget, fset=fset, doc=doc)


halo_struct_classes = {}

def load_plugin(layout):
    """Using an xml-defined layout, define a new Python class which wraps a c-struct"""

    def __init__(self, access, map_magic, halomap):
        self.access = access
        self.map_magic = map_magic
        self.halomap = halomap

        # remember fields for later printing
        self.field_names = []
        for node in layout:
            if 'name' in node.attrib:
                self.field_names.append(node.attrib['name'])

    def __str__(self):
        answer = '[%s]%%s' % layout.attrib['name']

        def stringify_struct(struct, answer, indent='\n    '):
            """Recursively stringifies the base struct as well as reflexives"""

            # fields sorted by xml declaration
            # should be sorted by offset but that's just convention
            for field in struct.field_names:
                value = getattr(struct, field)
                if type(value) == list:
                    for i, each in enumerate(value):
                        answer += indent + field + '[%d]:' % i
                        answer = stringify_struct(each, answer, indent + '    ')
                else:
                    answer += indent + field + ': ' + str(value)

            return answer

        return stringify_struct(self, answer) + '\n'

    # define a new class (aka type) without knowing the name ahead of time
    new_class = type(layout.attrib['name'], (object,), {})
    new_class.__init__ = __init__
    new_class.__str__ = __str__
    new_class.struct_size = int(layout.attrib['struct_size'], base=0)

    for node in layout:
        setattr(new_class, node.attrib['name'], make_property(node))

    # save entire plugins for later
    if layout.tag == 'plugin':
        halo_struct_classes[layout.attrib['name']] = new_class

    # reflexives are used immediately to help construct plugins
    else:
        return new_class

def load_plugins(plugin_dir):
    """Load all xml plugins from the plugin directory"""

    plugin_list = glob.glob(os.path.join(plugin_dir, '*.xml'))
    for filepath in plugin_list:
        root_struct = et.parse(filepath).getroot()  # load the xml definition
        load_plugin(root_struct)                    # create a class to read the struct as defined
