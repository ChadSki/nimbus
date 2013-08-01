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

import xml.etree.ElementTree as et
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

cdef extern from "stdlib.h" nogil:
    char *memcpy(char *dst, char *src, long len)
cdef extern from "string.h" nogil:
    long strlen(char *s)


def make_property(field):
    """Defines a property which reads/writes to a field in a plugin-defined struct"""

    if 'description' in field.attrib:
        doc = field.attrib['description']
    else:
        doc = field.attrib['name'].replace('_', ' ')

    def read_field(self):
        # retrieve the struct as bytes
        pybuffer = self.access.read_all_bytes()
        cdef:
            char *buf = <char *>(pybuffer)
            int offset = int(field.attrib['offset']) + self.offset

        # then cast the data into the correct format and return it
        answer = None
        if field.tag == 'float': answer = (<float *>(buf + offset))[0]
        elif field.tag == 'double': answer = (<double *>(buf + offset))[0]
        elif field.tag == 'int8': answer = (<int8_t *>(buf + offset))[0]
        elif field.tag == 'int16': answer = (<int16_t *>(buf + offset))[0]
        elif field.tag == 'int32': answer = (<int32_t *>(buf + offset))[0]
        elif field.tag == 'int64': answer = (<int64_t *>(buf + offset))[0]
        elif field.tag == 'uint8': answer = (<uint8_t *>(buf + offset))[0]
        elif field.tag == 'uint16': answer = (<uint16_t *>(buf + offset))[0]
        elif field.tag == 'uint32': answer = (<uint32_t *>(buf + offset))[0]
        elif field.tag == 'uint64': answer = (<uint64_t *>(buf + offset))[0]
        elif field.tag == 'ascii':
            # only copy up to null-termination, but limit to a maximum
            length = min(strlen(buf + offset), int(field.attrib['maxlength']))
            answer = b'\x00' * length
            memcpy(<char *>answer, buf + offset, length)
            if 'reverse' in field.attrib and field.attrib['reverse'] == 'true':
                answer = answer[::-1]
        return answer

    def write_field(self, value):
        # retrieve the struct as bytes
        pybuffer = self.access.read_all_bytes()
        cdef:
            int offset = int(field.attrib['offset']) + self.offset
            char *buf = <char *>(pybuffer)

        # cast the data into the correct format and write back
        if field.tag == 'float': (<float *>(buf + offset))[0] = value
        elif field.tag == 'double': (<double *>(buf + offset))[0] = value
        elif field.tag == 'int8': (<int8_t *>(buf + offset))[0] = value
        elif field.tag == 'int16': (<int16_t *>(buf + offset))[0] = value
        elif field.tag == 'int32': (<int32_t *>(buf + offset))[0] = value
        elif field.tag == 'int64': (<int64_t *>(buf + offset))[0] = value
        elif field.tag == 'uint8': (<uint8_t *>(buf + offset))[0] = value
        elif field.tag == 'uint16': (<uint16_t *>(buf + offset))[0] = value
        elif field.tag == 'uint32': (<uint32_t *>(buf + offset))[0] = value
        elif field.tag == 'uint64': (<uint64_t *>(buf + offset))[0] = value
        elif field.tag == 'ascii':
            if 'reverse' in field.attrib and field.attrib['reverse'] == 'true':
                value = value[::-1]
            memcpy(buf + offset, <char *>value, len(value))
            memcpy(buf + offset + len(value), <char *>b'\x00', 1)
        self.access.write_bytes(pybuffer, 0)

    return property(fget=read_field, fset=write_field, doc=doc)

def load_plugin(xml_filepath):
    """Using an xml definition, define a new Python class which wraps a c-struct"""

    base_struct = et.parse(xml_filepath).getroot()

    def __init__(self, access, offset=0):
        self.access = access
        self.offset = offset

    def __str__(self):
        # Example string representation:
        # struct type: map_header
        #   struct_size: 132
        #   integrity: b'daeh'
        #   game_version: 7
        #   map_size: 13523732
        #   index_offset: 8042316
        #   metadata_length: 5481416
        #   map_name: b'beavercreek'
        #   map_build: b'01.00.00.0564'
        #   map_type: 0

        answer = "struct type: " + base_struct.attrib['name']

        # attributes sorted by offset (confusing sort, I know...)
        for key in sorted(new_class.__dict__, key=lambda x: str(new_class.__dict__.get(x))):
            if key[0] != '_' and key != 'access':
                answer += '\n  ' + key + ': ' + str(getattr(self, key))
        return answer

    new_class = type(base_struct.attrib['name'], (object,), {})
    new_class.__init__ = __init__
    new_class.__str__ = __str__

    if 'size' in base_struct.attrib:
        new_class.struct_size = int(base_struct.attrib['size'])

    for field in base_struct:
        if 'name' in field.attrib:
            setattr(new_class, field.attrib['name'], make_property(field))

    return new_class
