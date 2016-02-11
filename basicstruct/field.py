# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import abc


class Field(metaclass=abc.ABCMeta):

    """Represents a single field within a struct, and brokers read/write access
    to the underlying bits wherever they may reside.

    Fields are parented by a struct, which can be accessed via `self.parent`.

    The getf/setf functions translate between Python values and raw data from
    `self.byteaccess`."""

    def __init__(self, *, offset, docstring, **kwargs):
        self.offset = offset
        self.docstring = docstring
        self.parent = None  # to be set by parent struct

    @property
    def byteaccess(self):
        """All reading and writing is brokered through the parent struct.
        This property enables convenient access, but the parent struct is
        the canonical owner of the ByteAccess."""
        try:
            return self.parent.byteaccess

        except AttributeError as exc:
            if parent is None:
                raise RuntimeError(
                    "This field is either not attached to a parent struct,"
                    "or for some other reason cannot read/write to its"
                    "byteaccess.") from exc
            else:
                raise exc

    @abc.abstractmethod
    def getf(self):
        """To define a new type of field, subclass Field and override
        this getter function."""
        pass

    @abc.abstractmethod
    def setf(self, value):
        """To define a new type of field, subclass Field and override
        this setter function."""
        pass


################################################################
# Text fields

class Ascii(Field):

    """Fixed-length ascii string."""

    def __init__(self, *, length, reverse=False, **kwargs):
        super().__init__(**kwargs)
        self.length = length
        self.reverse = reverse

    def getf(self):
        buf = self.byteaccess.read_ascii(self.offset, self.length)
        return buf[::-1] if self.reverse else buf

    def setf(self, newvalue):
        self.write_ascii(self.offset, self.length,
                         newvalue[::-1] if self.reverse else newvalue)


class Asciiz(Field):

    """Null-terminated ascii string."""

    def __init__(self, *, maxlength, **kwargs):
        super().__init__(**kwargs)
        self.maxlength = maxlength

    def getf(self):
        return self.byteaccess.read_asciiz(self.offset, self.maxlength),

    def setf(self, newvalue):
        self.byteaccess.write_asciiz(self.offset, self.maxlength, newvalue),


class AsciizPtr(Field):

    """Pointer to a null-terminated ascii string."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise NotImplementedError()

    def getf(self): pass

    def setf(self): pass


class RawData(Field):

    """Just bytes. Useful for debugging."""

    def __init__(self, *, length, **kwargs):
        super().__init__(**kwargs)
        self.length = length

    def getf(self):
        return self.byteaccess.read_bytes(self.offset, self.length)

    def setf(self, newvalue):
        self.byteaccess.WriteBytes(self.offset, newvalue)


################################################################
# Fields with options

class Enum16(Field):

    """16-bit enumeration of options."""

    def __init__(self, *, options, **kwargs):
        super().__init__(**kwargs)

        self.options = options
        # type: Dict[str, int]

        self.reverse_options = {
            int(number): name for name, number in options.items()
        }  # type: Dict[int, str]

        self.docstring = '\n'.join('    {} => {}'.format(number, name)
                                   for name, number in options.items())

        raise NotImplementedError()

    def fget(self):
        value = self.byteaccess.read_uint16(self.offset)
        try:
            return self.reverse_options[value]  # sometimes accessing throws

        except KeyError:
            print("enum16: Cannot find {} in options".format(value))
            return '???'  # Swallow exception, return placeholder

    def fset(self, newvalue):
        self.byteaccess.write_uint16(self.offset, self.options[newvalue])


class Flag(Field):

    """A boolean flag."""

    def __init__(self, *, bit, **kwargs):
        super().__init__(**kwargs)
        self.bit = bit

    def fget(self):
        return self.byteaccess.read_bit(self.offset, self.bit)

    def fset(self, newvalue):
        self.byteaccess.write_bit(self.offset, self.bit, newvalue)


################################################################
# Number fields


class Float32(Field):

    """Floating point single-precision number."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_float32(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_float32(self.offset, newvalue),


class Float64(Field):

    """Floating point double-precision number."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_float64(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_float64(self.offset, newvalue),


class Int8(Field):

    """8-bit (1-byte) signed integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_int8(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_int8(self.offset, newvalue)


class Int16(Field):

    """16-bit (2-byte) signed integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_int16(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_int16(self.offset, newvalue)


class Int32(Field):

    """32-bit (4-byte) signed integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_int32(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_int32(self.offset, newvalue)


class Int64(Field):

    """64-bit (8-byte) signed integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_int64(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_int64(self.offset, newvalue)


class UInt8(Field):

    """8-bit (1-byte) unsigned integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_uint8(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_uint8(self.offset, self.value)


class UInt16(Field):

    """16-bit (2-byte) unsigned integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_uint16(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_uint16(self.offset, self.value)


class UInt32(Field):

    """32-bit (4-byte) unsigned integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_uint32(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_uint32(self.offset, self.value)


class UInt64(Field):

    """64-bit (8-byte) unsigned integer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getf(self):
        return self.byteaccess.read_uint64(self.offset),

    def setf(self, newvalue):
        self.byteaccess.write_uint64(self.offset, self.value)
