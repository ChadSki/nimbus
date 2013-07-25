# cython: language_level=3
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

cdef extern from "stdlib.h" nogil:
    char *memcpy(char *dst, char *src, long len)
cdef extern from "string.h" nogil:
    long strlen(char *s)

import xml.etree.ElementTree as et

def make_property(field):
    """Defines a property which reads/writes from the host class's self.buffer"""

    if 'description' in field.attrib:
        doc = field.attrib['description']
    else:
        doc = field.attrib['name'].replace('_', ' ')

    def read_field(self):
        cdef:
            int offset = int(field.attrib['offset']) + self.offset
            char *buf = <char *>(self.buffer)

        answer = None

        if field.tag == 'ascii':
            # only copy up to null-termination, but limit to a maximum
            length = min(strlen(buf + offset), int(field.attrib['maxlength']))
            answer = b'\x00' * length
            memcpy(<char *>answer, buf + offset, length)

        elif field.tag == 'int8': answer = (<int8_t *>(buf + offset))[0]
        elif field.tag == 'int16': answer = (<int16_t *>(buf + offset))[0]
        elif field.tag == 'int32': answer = (<int32_t *>(buf + offset))[0]
        elif field.tag == 'int64': answer = (<int64_t *>(buf + offset))[0]

        elif field.tag == 'uint8': answer = (<uint8_t *>(buf + offset))[0]
        elif field.tag == 'uint16': answer = (<uint16_t *>(buf + offset))[0]
        elif field.tag == 'uint32': answer = (<uint32_t *>(buf + offset))[0]
        elif field.tag == 'uint64': answer = (<uint64_t *>(buf + offset))[0]

        return answer

    def write_field(self, value):
        cdef:
            int offset = int(field.attrib['offset']) + self.offset
            char *buf = <char *>(self.buffer)

        if field.tag == 'ascii':
            memcpy(buf + offset, <char *>value, len(value))
            memcpy(buf + offset + len(value), <char *>b'\x00', 1)

        elif field.tag == 'int8': (<int8_t *>(buf + offset))[0] = value
        elif field.tag == 'int16': (<int16_t *>(buf + offset))[0] = value
        elif field.tag == 'int32': (<int32_t *>(buf + offset))[0] = value
        elif field.tag == 'int64': (<int64_t *>(buf + offset))[0] = value

        elif field.tag == 'uint8': (<uint8_t *>(buf + offset))[0] = value
        elif field.tag == 'uint16': (<uint16_t *>(buf + offset))[0] = value
        elif field.tag == 'uint32': (<uint32_t *>(buf + offset))[0] = value
        elif field.tag == 'uint64': (<uint64_t *>(buf + offset))[0] = value

    return property(fget=read_field, fset=write_field, doc=doc)

def load_plugin(xml_filepath):
    """Using an xml definition, define a new Python class which wraps a c-struct"""

    base_struct = et.parse(xml_filepath).getroot()

    new_class = type(base_struct.attrib['name'], (object,), {'struct_size': int(base_struct.attrib['size'])})

    def constructor(self, buffer, offset=0):
        self.buffer = buffer
        self.offset = offset

    def to_str(self):
        answer = "struct type: " + base_struct.attrib['name']

        # interestingly this sorts the raw lambdas, but effectively sorts by offset,
        # probably because that's the order we defined them in
        for key in sorted(new_class.__dict__, key=lambda x: str(new_class.__dict__.get(x))):
            if key[0] != '_' and key != 'buffer':
                answer += '\n  ' + key + ': ' + str(getattr(self, key))
        
        return answer

    new_class.__init__ = constructor
    new_class.__str__ = to_str

    for field in base_struct:
        if 'name' in field.attrib:
            setattr(new_class, field.attrib['name'], make_property(field))

    return new_class
