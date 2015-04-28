# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import functools


class NotifyProperty(property):

    """Triggers a notification when the value is changed by a set operation."""

    def __init__(self, *args, fset, name, **kwargs):

        def newsetter(slf, newvalue):
            """Wrap the setter with a notification check"""
            oldvalue = slf.fget(slf)
            if oldvalue != newvalue:
                fset(slf, newvalue)
                slf.property_changed(self.name)

        super(NotifyProperty, self).__init__(*args, fset=newsetter, **kwargs)
        self.name = name


################################################################
# Text fields

def ascii(*, name, offset, length, reverse, info=''):
    """Fixed-length ascii string."""

    def fget(self):
        buf = self.byteaccess.read_ascii(offset, length)
        return buf[::-1] if reverse else buf

    def fset(self, value):
        self.write_ascii(offset, length,
                         value[::-1] if reverse else value)

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info)


def asciiz(*, name, offset, maxlength, info=''):
    """Null-terminated ascii string."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_asciiz(offset, maxlength),
        fset=lambda self, value: self.byteaccess.write_asciiz(offset, maxlength, value),
        name=name, doc=info)


def rawdata(*, name, offset, length, info=''):
    """Just bytes. Useful for debugging."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.ReadBytes(offset, length),
        fset=lambda self, value: self.byteaccess.WriteBytes(offset, value),
        name=name, doc=info)


################################################################
# Halo-specific fields

def reference(*, name, offset, loneid='False', info=''):
    """Semantic link to a HaloTag."""

    if loneid not in ('True', 'False'):
        raise ValueError(
            'LoneID attribute set to "{}", must be "True" or "False".'.format(loneid))

    # LoneIDs (idents just by themselves) need no adjustment.
    if loneid != 'True':
        # This is a full reference, and we only care to read the ident
        offset += 12  # (which is located 12 bytes inside)

    def fget(self):
        ident = self.byteaccess.read_uint32(offset)
        if ident == 0 or ident == 0xFFFFFFFF:
            return None
        try:
            return self.halomap.tags_by_ident[ident]  # the referenced tag
        except KeyError:
            # we wanted a tag that wasn't there =(
            return None

    def fset(self, value):
        # when value is None, write Halo's version of null (-1)
        # otherwise, write the tag's ident, not the tag itself
        self.byteaccess.write_uint32(offset,
                                     0xFFFFFFFF if value is None
                                     else value.ident)

    return NotifyProperty(name=name, fget=fget, fset=fset, doc=info)


def struct_array(*, name, offset, struct_class, info=''):
    """A pointer to an array of structs."""

    def fget(self):
        count = self.byteaccess.read_uint32(offset)
        raw_offset = self.byteaccess.read_uint32(offset + 4)

        start_offset = raw_offset - self.halomap.magic
        size = struct_class.struct_size

        if count > 1024:  # something's fucky
            raise RuntimeError('{} structs in struct_array?!'.format(count))

        return [struct_class(self.halomap.context.ByteAccess(
                                start_offset + i * size, size),
                             self.halomap)
                for i in range(count)]

    def fset(self, value):
        raise NotImplementedError(
            'Assigning entire struct arrays is not yet supported.')

    return NotifyProperty(name=name, fget=fget, fset=fset, doc=info)


################################################################
# Fields with options

def enum16(*, name, offset, options, info=''):
    """16-bit enumeration of options."""

    forward_options = {
        int(number): name for name, number in options.items()
    }  # type: Dict[int, str]

    reversed_options = {
        name: int(number) for name, number in options.items()
    }  # type: Dict[str, int]

    doc = '\n'.join('    {} => {}'.format(number, name)
                    for name, number in options.items())

    def fget(self):
        try:
            value = self.byteaccess.read_uint16(offset)
            return forward_options[value]
        except KeyError:
            print("enum16: Cannot find {} in options for {}".format(value, name))
            return '???'  # Swallow exception, return placeholder

    def fset(self, value):
        self.byteaccess.write_uint16(offset, reversed_options[value])

    return NotifyProperty(fget=fget, fset=fset, name=name, doc=info+doc)


def flag(*, name, offset, bit, info=''):
    """A boolean flag."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_bit(offset, bit),
        fset=lambda self, value: self.byteaccess.write_bit(offset, bit, value),
        name=name, doc=info)


################################################################
# Number fields


def float32(*, name, offset, info=''):
    """Floating point single-precision number."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_float32(offset),
        fset=lambda self, value: self.byteaccess.write_float32(offset, value),
        name=name, doc=info)


def float64(*, name, offset, info):
    """Floating point double-precision number."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_float64(offset),
        fset=lambda self, value: self.byteaccess.write_float64(offset, value),
        name=name, doc=info)


def int8(*, name, offset, info=''):
    """8-bit (1-byte) signed integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_int8(offset),
        fset=lambda self, value: self.byteaccess.write_int8(offset, value),
        name=name, doc=info)


def int16(*, name, offset, info=''):
    """16-bit (2-byte) signed integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_int16(offset),
        fset=lambda self, value: self.byteaccess.write_int16(offset, value),
        name=name, doc=info)


def int32(*, name, offset, info=''):
    """32-bit (4-byte) signed integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_int32(offset),
        fset=lambda self, value: self.byteaccess.write_int32(offset, value),
        name=name, doc=info)


def int64(*, name, offset, info=''):
    """64-bit (8-byte) signed integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_int64(offset),
        fset=lambda self, value: self.byteaccess.write_int64(offset, value),
        name=name, doc=info)


def uint8(*, name, offset, info=''):
    """8-bit (1-byte) unsigned integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_uint8(offset),
        fset=lambda self, value: self.byteaccess.write_uint8(offset, value),
        name=name, doc=info)


def uint16(*, name, offset, info=''):
    """16-bit (2-byte) unsigned integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_uint16(offset),
        fset=lambda self, value: self.byteaccess.write_uint16(offset, value),
        name=name, doc=info)


def uint32(*, name, offset, info=''):
    """32-bit (4-byte) unsigned integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_uint32(offset),
        fset=lambda self, value: self.byteaccess.write_uint32(offset, value),
        name=name, doc=info)


def uint64(*, name, offset, info=''):
    """64-bit (8-byte) unsigned integer."""
    return NotifyProperty(
        fget=lambda self: self.byteaccess.read_uint64(offset),
        fset=lambda self, value: self.byteaccess.write_uint64(offset, value),
        name=name, doc=info)


# End fields
################################################################

@functools.lru_cache()
def field_type(typename):
    """Import a field plugin and return its constructor.

    Field types are constantly reused, so this function is cached."""
    return NotImplementedError()
