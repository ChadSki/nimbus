# cython: language_level=3

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
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

cdef extern from "stdlib.h" nogil:
    char* memcpy(char* dst, char* src, long len)
cdef extern from "string.h" nogil:
    long strlen(char* s)

def py_strlen(s): return strlen(<char*>s)

def make_property(field):
    """Defines a property which reads/writes to a field in a plugin-defined struct"""

    # to make a property we need three things:
    #  1) a getter function
    #  2) a setter function
    #  3) a docstring (optional)

    def make_fget():
        """Defines a custom fget depending on what type of reader is needed"""

        # We need different ways to read the data depending on what type of field
        # this is. Define all possible readers here, then pick one later.

        # Cython is a little different than C. We can't expect pointers,
        # so we need to cast before dereferencing.
        # Note that 'int' is just a Cython hint, it doesn't have a specific size
        def read_float(self, int address):  return (<float*>address)[0]
        def read_double(self, int address): return (<double*>address)[0]
        def read_int8(self, int address):   return (<int8_t*>address)[0]
        def read_int16(self, int address):  return (<int16_t*>address)[0]
        def read_int32(self, int address):  return (<int32_t*>address)[0]
        def read_int64(self, int address):  return (<int64_t*>address)[0]
        def read_uint8(self, int address):  return (<uint8_t*>address)[0]
        def read_uint16(self, int address): return (<uint16_t*>address)[0]
        def read_uint32(self, int address): return (<uint32_t*>address)[0]
        def read_uint64(self, int address): return (<uint64_t*>address)[0]

        def read_ascii(self, int address):
            """Reads a fixed-length ascii string"""

            length = int(field.attrib['length'])            # the fixed length to copy
            answer = b'\x00' * length                       # create a new Python string
            memcpy(<char*>answer, <char*>address, length)   # copy the data over

            # 'ihev' <-> 'vehi' and so forth
            if 'reverse' in field.attrib and field.attrib['reverse'] == 'true':
                answer = answer[::-1]

            return answer.decode('ascii')

        def read_asciiz(self, int address):
            """Reads a null-terminated ascii string"""

            # only copy up to null-termination, but limit to a maximum
            length = min(strlen(<char*>address), int(field.attrib['maxlength']))

            answer = b'\x00' * length                       # create a new Python string
            memcpy(<char*>answer, <char*>address, length)   # copy the data over

            return answer.decode('ascii')

        # select the appropriate reader for this property's type
        read_field = {
            'float' : read_float,
            'double' : read_double,
            'int8' : read_int8,
            'int16' : read_int16,
            'int32' : read_int32,
            'int64' : read_int64,
            'uint8' : read_uint8,
            'uint16' : read_uint16,
            'uint32' : read_uint32,
            'uint64' : read_uint64,
            'ascii' : read_ascii,
            'asciiz' : read_asciiz,
        }[field.tag]

        cdef int offset = int(field.attrib['offset'])   # get the field's offset from xml

        def fget(self):
            pybuffer = self.access.read_all_bytes()     # retrieve the struct as bytes
            cdef int buf = <int>(<char*>(pybuffer))     # Cython cast for pointer arithmetic
            return read_field(self, buf + offset)       # reinterpret the raw data with the selected reader

        return fget

    def make_fset():
        """Defines a custom fset depending on what type of writer is needed"""

        # We need different ways to write the data depending on what type of field
        # this is. Define all possible writers here, then pick one later.

        # Cython is a little different than C. We can't expect pointers,
        # so we need to cast before dereferencing then setting the value.
        # Note that 'int' is just a Cython hint, it doesn't have a specific size
        def write_float(self, int address, value):  (<float*>address)[0] = value
        def write_double(self, int address, value): (<double*>address)[0] = value
        def write_int8(self, int address, value):   (<int8_t*>address)[0] = value
        def write_int16(self, int address, value):  (<int16_t*>address)[0] = value
        def write_int32(self, int address, value):  (<int32_t*>address)[0] = value
        def write_int64(self, int address, value):  (<int64_t*>address)[0] = value
        def write_uint8(self, int address, value):  (<uint8_t*>address)[0] = value
        def write_uint16(self, int address, value): (<uint16_t*>address)[0] = value
        def write_uint32(self, int address, value): (<uint32_t*>address)[0] = value
        def write_uint64(self, int address, value): (<uint64_t*>address)[0] = value

        def write_ascii(self, int address, value):
            """Writes a fixed-length ascii string"""
            value = value.encode('ascii')                   # convert from string to bytes

            # 'ihev' <-> 'vehi' and so forth
            if 'reverse' in field.attrib and field.attrib['reverse'] == 'true':
                value = value[::-1]

            length = int(field.attrib['length'])            # the fixed length to copy
            memcpy(<char*>address, <char*>value, length)    # copy the data over

        def write_asciiz(self, int address, value):
            """Writes a null-terminated ascii string"""
            value = value.encode('ascii')                   # convert from string to bytes

            # only copy up to null-termination, but limit to a maximum (account for null terminator)
            length = min(strlen(<char*>value), int(field.attrib['maxlength']) - 1)

            memcpy(<char*>address, <char*>value, length)    # copy the data over
            null_loc = address + length                     # calculate address of the null-terminator
            memcpy(<char*>null_loc, <char*>b'\x00', 1)      # null-terminate

        # select the appropriate writer for this property's type
        write_field = {
            'float' : write_float,
            'double' : write_double,
            'int8' : write_int8,
            'int16' : write_int16,
            'int32' : write_int32,
            'int64' : write_int64,
            'uint8' : write_uint8,
            'uint16' : write_uint16,
            'uint32' : write_uint32,
            'uint64' : write_uint64,
            'ascii' : write_ascii,
            'asciiz' : write_asciiz,
        }[field.tag]

        cdef int offset = int(field.attrib['offset'])   # get the field's offset from xml

        def fset(self, value):
            pybuffer = self.access.read_all_bytes()     # retrieve the struct as bytes
            cdef char* buf = <char*>(pybuffer)          # Cython cast for pointer arithmetic
            write_field(self, buf + offset, value)      # write the new value by using the selected writer
            self.access.write_bytes(pybuffer, 0)        # don't forget to write the bytes back!

        return fset

    if 'description' in field.attrib:
        doc = field.attrib['description']
    else:
        doc = field.attrib['name'].replace('_', ' ')

    return property(fget=make_fget(), fset=make_fset(), doc=doc)


plugin_dict = {}

def load_plugin(xml_filepath):
    """Using an xml definition, define a new Python class which wraps a c-struct"""

    # load the xml definition
    root_struct = et.parse(xml_filepath).getroot()

    def __init__(self, access):
        self.access = access

        # remember fields for later printing
        self.field_names = []
        for field in root_struct:
            if 'name' in field.attrib:
                self.field_names.append(field.attrib['name'])

    def __str__(self):
        answer = "struct type: " + root_struct.attrib['name']

        # fields sorted by xml declaration
        # should be sorted by offset but that's just convention
        for key in self.field_names:
            answer += '\n  ' + key + ': ' + str(getattr(self, key))

        return answer

    # define a new class (aka type) without knowing the name ahead of time
    new_class = type(root_struct.attrib['name'], (object,), {})
    new_class.__init__ = __init__
    new_class.__str__ = __str__

    if 'size' in root_struct.attrib:
        new_class.struct_size = int(root_struct.attrib['size'])

    for field in root_struct:
        if 'name' in field.attrib:
            setattr(new_class, field.attrib['name'], make_property(field))

    plugin_dict[root_struct.attrib['name']] = new_class
    return new_class

def load_plugins(plugin_dir):
    plugins = glob.glob(os.path.join(plugin_dir,'*.xml'))
    for each in plugins:
        load_plugin(each)
