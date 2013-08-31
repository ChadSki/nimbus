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

cdef extern from "stdlib.h" nogil:
    char* memcpy(char* dst, char* src, long len)

cdef extern from "string.h" nogil:
    long strlen(char* s)

def py_strlen(s):
    return strlen(<char*>s)


cdef class Field(object):
    """Fields read and write to C structs in a way that Python can understand.
    Use a subclass of Field to read/write a specific datatype."""

    cdef int offset

    def __init__(self, **kwargs):
        pass

    def get_value(self, pybuffer):
        return self._get_value(<int><char*>pybuffer)

    def set_value(self, pybuffer, value):
        self._set_value(<int><char*>pybuffer, value)

    def _get_value(self, int address):
        raise Exception("Cannot read from an abstract Field")

    def _set_value(self, int address):
        raise Exception("Cannot write to an abstract Field")


# Primitives are straightforward to read and write, even though Cython is a little
# different than C. We can't expect pointers, so we need to cast before dereferencing.

# Note that using 'int' for pointers is just a Cython hint; it doesn't require a specific size

cdef class FloatField(Field):
    def _get_value(self, int address): return (<float*>(address))[0]
    def _set_value(self, int address, value): (<float*>(address))[0] = value

cdef class DoubleField(Field):
    def _get_value(self, int address): return (<double*>(address))[0]
    def _set_value(self, int address, value): (<double*>(address))[0] = value

cdef class Int8Field(Field):
    def _get_value(self, int address): return (<int8_t*>(address))[0]
    def _set_value(self, int address, value): (<int8_t*>(address))[0] = value

cdef class Int16Field(Field):
    def _get_value(self, int address): return (<int16_t*>(address))[0]
    def _set_value(self, int address, value): (<int16_t*>(address))[0] = value

cdef class Int32Field(Field):
    def _get_value(self, int address): return (<int32_t*>(address))[0]
    def _set_value(self, int address, value): (<int32_t*>(address))[0] = value

cdef class Int64Field(Field):
    def _get_value(self, int address): return (<int64_t*>(address))[0]
    def _set_value(self, int address, value): (<int64_t*>(address))[0] = value

cdef class UInt8Field(Field):
    def _get_value(self, int address): return (<uint8_t*>(address))[0]
    def _set_value(self, int address, value): (<uint8_t*>(address))[0] = value

cdef class UInt16Field(Field):
    def _get_value(self, int address): return (<uint16_t*>(address))[0]
    def _set_value(self, int address, value): (<uint16_t*>(address))[0] = value

cdef class UInt32Field(Field):
    def _get_value(self, int address): return (<uint32_t*>(address))[0]
    def _set_value(self, int address, value): (<uint32_t*>(address))[0] = value

cdef class UInt64Field(Field):
    def _get_value(self, int address): return (<uint64_t*>(address))[0]
    def _set_value(self, int address, value): (<uint64_t*>(address))[0] = value


cdef class AsciiField(Field):
    """Read/write fixed length ascii strings"""

    cdef:
        int length
        object reverse

    def __init__(self, **kwargs):
        self.length = int(kwargs.pop('length'), base=0)
        self.reverse = kwargs.pop('reverse', 'false')
        super(AsciiField, self).__init__(**kwargs)

    def _get_value(self, int address):
        answer = b'\x00' * self.length                      # create a new Python bytestring
        memcpy(<char*>answer, <char*>address, self.length)  # copy the data over
        answer = answer.decode('ascii')                     # convert from bytestring to string

        if self.reverse == 'true':
            answer = answer[::-1]

        return answer

    def _set_value(self, int address, value):
        if self.reverse == 'true':
            value = value[::-1]

        value = value.encode('ascii')                       # convert from string to bytes
        memcpy(<char*>address, <char*>value, self.length)   # copy the data over

cdef class AsciizField(Field):
    """Read/write null-terminated ascii strings"""

    cdef int maxlength

    def __init__(self, **kwargs):
        self.maxlength = int(kwargs.pop('maxlength'), base=0)
        super(AsciizField, self).__init__(**kwargs)

    def _get_value(self, int address):
        # only copy up to null-termination, but limit to a maximum
        length = min(strlen(<char*>address), self.maxlength)

        answer = b'\x00' * length                           # create a new Python bytestring
        memcpy(<char*>answer, <char*>address, length)       # copy the data over

        return answer.decode('ascii')

    def _set_value(self, int address, value):
        value = value.encode('ascii')                       # convert from string to bytes

        # only copy up to null-termination, but limit to a maximum
        # also leave the last byte for a null character
        self.length = min(strlen(<char*>value), self.maxlength - 1)

        memcpy(<char*>address, <char*>value, self.length)   # copy the data over
        null_loc = address + self.length                    # calculate address of the null-terminator
        memcpy(<char*>null_loc, <char*>b'\x00', 1)          # null-terminate

cdef class ReflexiveField(Field):
    cdef:
        object count_reader
        object pointer_reader

    def __init__(self, **kwargs):
        super(ReflexiveField, self).__init__(**kwargs)
        self.count_reader = UInt32Field(offset=self.offset)
        self.pointer_reader = UInt32Field(offset=(self.offset + 4))

    def _get_value(self, int address):
        count = self.count_reader.get_value(address)
        p_curr = self.pointer_reader.get_value(address)

        for i in range(count):
            reflexive = object()
            for child in self.children:
                pass
