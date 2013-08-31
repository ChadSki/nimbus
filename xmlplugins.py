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
from field import *


def make_property(field):
    """Defines a property which reads/writes to a field in a plugin-defined struct"""

    # to make a property we need three things:
    #  1) a getter function
    #  2) a setter function
    #  3) a docstring (optional)

    converter = {
        'float' : FloatField,
        'double' : DoubleField,
        'int8' : Int8Field,
        'int16' : Int16Field,
        'int32' : Int32Field,
        'int64' : Int64Field,
        'uint8' : UInt8Field,
        'uint16' : UInt16Field,
        'uint32' : UInt32Field,
        'uint64' : UInt64Field,
        'ascii' : AsciiField,
        'asciiz' : AsciizField,
    }[field.tag](**field.attrib)

    def fget(self):
        buf = self.access.read_all_bytes()  # retrieve the struct as bytes
        return converter.get_value(buf)     # reinterpret the raw data with the selected reader

    def fset(self, value):
        buf = self.access.read_all_bytes()  # retrieve the struct as bytes
        converter.set_value(buf)            # write the new value by using the selected writer
        self.access.write_bytes(buf, 0)     # don't forget to write the bytes back!

        return fset

    if 'description' in field.attrib:
        doc = field.attrib['description']
    else:
        doc = field.attrib['name'].replace('_', ' ')

    return property(fget=fget, fset=fset, doc=doc)


struct_reader = {}

def load_plugin(layout):
    """Using an xml-defined layout, define a new Python class which wraps a c-struct"""

    def __init__(self, access):
        self.access = access

        # remember fields for later printing
        self.field_names = []
        for field in layout:
            if 'name' in field.attrib:
                self.field_names.append(field.attrib['name'])

    def __str__(self):
        answer = "struct type: " + layout.attrib['name']

        # fields sorted by xml declaration
        # should be sorted by offset but that's just convention
        for key in self.field_names:
            answer += '\n  ' + key + ': ' + str(getattr(self, key))

        return answer

    # define a new class (aka type) without knowing the name ahead of time
    new_class = type(layout.attrib['name'], (object,), {})
    new_class.__init__ = __init__
    new_class.__str__ = __str__

    if 'size' in layout.attrib:
        new_class.struct_size = int(layout.attrib['size'])

    for field in layout:
        setattr(new_class, field.attrib['name'], make_property(field))

    struct_reader[layout.attrib['name']] = new_class

def load_plugins(plugin_dir):
    """Load all xml plugins from the plugin directory"""

    plugin_list = glob.glob(os.path.join(plugin_dir, '*.xml'))
    for filepath in plugin_list:
        root_struct = et.parse(filepath).getroot()  # load the xml definition
        load_plugin(root_struct)                    # create a class to read the struct as defined
