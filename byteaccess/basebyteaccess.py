# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import abc
from struct import pack, unpack


class BaseByteAccess(metaclass=abc.ABCMeta):

    """Abstract base class implements common ByteAccess functionality."""

    def __init__(self, offset, size):
        """Provide access to a region of bytes.

        offset -- Absolute offset within the source medium.
        size -- Number of bytes to grant access to.
        """
        self.offset = offset
        self.size = size

    # This abstract class is defined such that subclasses only need to
    # implement the following two methods:

    @abc.abstractmethod
    def _read_bytes(self, offset, size):
        pass

    @abc.abstractmethod
    def _write_bytes(self, offset, to_write):
        pass

    # Bytestrings

    def read_bytes(self, offset, size):
        """Read a number of bytes from the source.

        offset -- Relative offset within the ByteAccess.
        size -- Number of bytes to read.
        """
        if offset + size > self.size:
            raise ValueError("Cannot read past end of ByteAccess. " +
                             "offset:{0} size:{1} self.size:{2}"
                             .format(offset, size, self.size))

        return self._read_bytes(offset, size)

    def read_all_bytes(self):
        """Read all data this ByteAccess encapsulates."""
        return self.read_bytes(0, self.size)

    def write_bytes(self, offset, to_write):
        """Write a bytestring to the source.

        offset -- Relative offset within the ByteAccess.
        to_write -- The bytestring to write. If the bytestring is too long to
                    write at the specified offset, raises ValueError.
        """
        if offset + len(to_write) > self.size:
            raise ValueError("Cannot write past end of ByteAccess. " +
                             "offset:{0} size:{1} self.size:{2}"
                             .format(offset, len(to_write), self.size))

        self._write_bytes(offset, to_write)

    # Strings

    def read_ascii(self, offset, length, reverse=False):
        buf = self.read_bytes(offset, length).decode('ascii')
        return buf[::-1] if reverse else buf

    def write_ascii(self, offset, data, reverse=False,):
        buf = data.encode('ascii')
        self.write_bytes(offset, buf[::-1] if reverse else buf)

    def read_asciiz(self, offset, length):
        buf = self.read_bytes(offset, length).decode('ascii')
        return buf[:buf.find('\0')]  # null-terminated

    def write_asciiz(self, offset, data):
        buf = (data + '\0').encode('ascii')
        self.write_bytes(offset, buf)

    # TODO - should these be named 'utf-16z' to indicate they are null-terminated?

    def read_utf16(self, offset, length):
        buf = self.read_bytes(offset, length).decode('utf-16')
        return buf[:buf.find('\0')]  # null-terminated

    def write_utf16(self, offset, data):
        buf = (data + '\0').encode('utf-16')
        self.write_bytes(offset, buf)

    # Numerics

    def read_float32( self, offset): return unpack('<f', self.read_bytes(offset, 4))[0]
    def read_float64( self, offset): return unpack('<d', self.read_bytes(offset, 8))[0]
    def read_int8(    self, offset): return unpack('<b', self.read_bytes(offset, 1))[0]
    def read_int16(   self, offset): return unpack('<h', self.read_bytes(offset, 2))[0]
    def read_int32(   self, offset): return unpack('<i', self.read_bytes(offset, 4))[0]
    def read_int64(   self, offset): return unpack('<q', self.read_bytes(offset, 8))[0]
    def read_uint8(   self, offset): return unpack('<B', self.read_bytes(offset, 1))[0]
    def read_uint16(  self, offset): return unpack('<H', self.read_bytes(offset, 2))[0]
    def read_uint32(  self, offset): return unpack('<I', self.read_bytes(offset, 4))[0]
    def read_uint64(  self, offset): return unpack('<Q', self.read_bytes(offset, 8))[0]
    def write_float32(self, offset, data): self.write_bytes(offset, pack('<f', data))
    def write_float64(self, offset, data): self.write_bytes(offset, pack('<d', data))
    def write_int8(   self, offset, data): self.write_bytes(offset, pack('<b', data))
    def write_int16(  self, offset, data): self.write_bytes(offset, pack('<h', data))
    def write_int32(  self, offset, data): self.write_bytes(offset, pack('<i', data))
    def write_int64(  self, offset, data): self.write_bytes(offset, pack('<q', data))
    def write_uint8(  self, offset, data): self.write_bytes(offset, pack('<B', data))
    def write_uint16( self, offset, data): self.write_bytes(offset, pack('<H', data))
    def write_uint32( self, offset, data): self.write_bytes(offset, pack('<I', data))
    def write_uint64( self, offset, data): self.write_bytes(offset, pack('<Q', data))
