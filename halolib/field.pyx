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

from libc.stdint cimport int8_t, int16_t, int32_t, int64_t
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

__all__ = ['py_strlen', 'make_field_property']


cdef extern from "stdlib.h" nogil:
    char* memcpy(char* dst, char* src, long len)

cdef extern from "string.h" nogil:
    long strlen(char* s)

def py_strlen(s):
    return strlen(<char*>s)

# ----------------------------------------------------------------
# Get primitive values from pointer location

def read_float32(int address): return (<float*>address)[0]
def read_float64(int address): return (<double*>address)[0]
def read_int8(int address):    return (<int8_t*>address)[0]
def read_int16(int address):   return (<int16_t*>address)[0]
def read_int32(int address):   return (<int32_t*>address)[0]
def read_int64(int address):   return (<int64_t*>address)[0]
def read_uint8(int address):   return (<uint8_t*>address)[0]
def read_uint16(int address):  return (<uint16_t*>address)[0]
def read_uint32(int address):  return (<uint32_t*>address)[0]
def read_uint64(int address):  return (<uint64_t*>address)[0]

# ----------------------------------------------------------------
# Assign primitive values to pointer location

def write_float32(int address, float value): (<float*>address)[0] = value
def write_float64(int address, float value): (<double*>address)[0] = value
def write_int8(int address, int value):      (<int8_t*>address)[0] = value
def write_int16(int address, int value):     (<int16_t*>address)[0] = value
def write_int32(int address, int value):     (<int32_t*>address)[0] = value
def write_int64(int address, int value):     (<int64_t*>address)[0] = value
def write_uint8(int address, int value):     (<uint8_t*>address)[0] = value
def write_uint16(int address, int value):    (<uint16_t*>address)[0] = value
def write_uint32(int address, int value):    (<uint32_t*>address)[0] = value
def write_uint64(int address, int value):    (<uint64_t*>address)[0] = value


def make_field_property(node, chunk_class=None):
    """Defines a property which reads/writes to a field in a plugin-defined chunk"""

    # to make a property we need three things:
    #  1) a getter function
    #  2) a setter function
    #  3) a docstring (optional)

    offset = int(node.attrib['offset'], base=0)

    if node.tag == 'reflexive':
        def fget(chunk_self):
            buf = chunk_self.access.read_bytes(offset, 8)
            count = read_uint32(<int><char*>buf)
            raw_offset = read_uint32(<int><char*>buf + 4)

            structs = []
            curr_p = raw_offset - chunk_self.map_magic
            for i in range(count):
                structs.append(chunk_class(chunk_self.access.__class__(curr_p, chunk_class.struct_size), chunk_self.map_magic, chunk_self.halomap))
                curr_p += chunk_class.struct_size

            return structs

        def fset(chunk_self, value):
            raise Exception("Not yet implemented")

    elif node.tag == 'reference':
        offset += 12 # since we only care to read the ident, 12 bytes into a reference

        def fget(chunk_self):
            buf = chunk_self.access.read_bytes(offset, 4)
            ident = read_uint32(<int><char*>buf)

            if ident == 0 or ident == 0xFFFFFFFF:
                return None
            else:
                return chunk_self.halomap.tags[ident]   # return the referenced tag

        def fset(chunk_self, value):
            if value:
                ident = value.ident                     # write back the tag's ident, not the tag itchunk_self
            else:
                ident = 0xFFFFFFFF                      # Halo's version of null

            buf = chunk_self.access.read_bytes(offset, 4)
            write_uint32(<int><char*>buf, ident)
            chunk_self.access.write_bytes(buf, offset)

    # both of these are fixed-length bytestrings, but ascii is decoded
    # from bytes to a Python string
    elif node.tag in ['rawdata', 'ascii']:
        length = int(node.attrib.get('length', '0'), base=0)
        reverse = node.attrib.get('reverse', 'false')

        def fget(chunk_self):
            buf = chunk_self.access.read_bytes(offset, length)
            answer = b'\x00' * length
            memcpy(<char*>answer, <char*>buf, length)

            if node.tag == 'ascii': answer = answer.decode('ascii')
            if reverse == 'true': answer = answer[::-1]
            return answer

        def fset(chunk_self, value):
            if reverse == 'true': value = value[::-1]
            if node.tag == 'ascii': value = value.encode('ascii')

            buf = chunk_self.access.read_bytes(offset, length)
            memcpy(<char*>buf, <char*>value, length)
            chunk_self.access.write_bytes(buf, offset)

    # null-terminated strings are a bit different
    elif node.tag == 'asciiz':
        maxlength = int(node.attrib.get('maxlength', '0'), base=0)

        def fget(chunk_self):
            buf = chunk_self.access.read_bytes(offset, maxlength)

            # stop at null-termination, but limit to a maximum
            length = min(strlen(<char*>buf), maxlength)

            answer = b'\x00' * length
            memcpy(<char*>answer, <char*>buf, length)
            return answer.decode('ascii')

        def fset(chunk_self, value):
            # stop at null-termination, but limit to a maximum
            # (leaving the last byte for a null character)
            length = min(strlen(<char*>value), maxlength - 1)

            buf = chunk_self.access.read_bytes(offset, length)
            memcpy(<char*>buf, <char*>value, length)
            null_loc = <int><char*>buf + length
            memcpy(<char*>null_loc, <char*>b'\x00', 1)
            chunk_self.access.write_bytes(buf, offset)

    else: # primitives
        read_fn, write_fn, size_of = {
            'float32': (read_float32, write_float32, 4),
            'float64': (read_float64, write_float64, 8),
            'int8':    (read_int8,    write_int8,    1),
            'int16':   (read_int16,   write_int16,   2),
            'int32':   (read_int32,   write_int32,   4),
            'int64':   (read_int64,   write_int64,   8),
            'uint8':   (read_uint8,   write_uint8,   1),
            'uint16':  (read_uint16,  write_uint16,  2),
            'uint32':  (read_uint32,  write_uint32,  4),
            'uint64':  (read_uint64,  write_uint64,  8),
        }[node.tag]

        def fget(chunk_self):
            buf = chunk_self.access.read_bytes(offset, size_of)
            return read_fn(<int><char*>buf)

        def fset(chunk_self, value):
            buf = chunk_self.access.read_bytes(offset, size_of)
            write_fn(<int><char*>buf, value)
            chunk_self.access.write_bytes(buf, offset)

    if 'description' in node.attrib:
        doc = node.attrib['description']
    else:
        doc = node.attrib['name'].replace('_', ' ')

    return property(fget=fget, fset=fset, doc=doc)
