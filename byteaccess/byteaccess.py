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

class ByteAccess(object):
    """Cordons off an area of bytes. Within a ByteAccess, offsets are
    relative, and attempting to read or write outside the encapsulated
    area will raise an Exception."""

    def __init__(self, offset, size):
        self.offset = offset
        self.size = size

    def create_subaccess(self, offset, size):
        #relative_offset = offset - self.offset
        #if relative_offset + size > self.size:
        #    raise Exception("Cannot subaccess past end of Access. offset:%d size:%d self.size:%d" % (relative_offset, size, self.size))

        return self._create_subaccess(offset, size)

    def read_bytes(self, offset, size):
        if offset + size > self.size:
            raise Exception("Cannot read past end of Access. offset:%d size:%d self.size:%d" % (offset, size, self.size))

        return self._read_bytes(offset, size)

    def read_all_bytes(self):
        return self.read_bytes(0, self.size)

    def write_bytes(self, to_write, offset):
        if offset + len(to_write) > self.size:
            raise Exception("Cannot write past end of Access. offset:%d size:%d self.size:%d" % (offset, size, self.size))

        self._write_bytes(to_write, offset)

    # This abstract class is defined such that subclasses only need to
    # implement the following two methods:

    def _read_bytes(self, offset, size):
        raise Exception("Reading not implemented in abstract class")

    def _write_bytes(self, to_write, offset):
        raise Exception("Writing not implemented in abstract class")


class FileAccess(ByteAccess):
    """Encapsulates reading and writing to a memory-mapped file on disk."""

    def __init__(self, mmap_f, offset, size):
        self.mmap_f = mmap_f
        super(FileAccess, self).__init__(offset, size)

    def _create_subaccess(self, offset, size):
        return FileAccess(self.mmap_f, offset, size)

    def _read_bytes(self, offset, size):
        begin = self.offset + offset
        end = begin + size
        return self.mmap_f[begin:end]

    def _write_bytes(self, to_write, offset):
        begin = self.offset + offset
        end = begin + len(to_write)
        self.mmap_f[begin:end] = to_write
