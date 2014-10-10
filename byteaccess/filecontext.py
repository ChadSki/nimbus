# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .basebyteaccess import BaseByteAccess


class FileContext(object):

    """Context for creating ByteAccesses which read and write to a specific file."""

    def __init__(self, filepath):
        """Instantiate a WinMemContext for creating ByteAccesses.

        filepath -- Full path to the file which will be opened.
        """
        import mmap

        self.file_handle = open(filepath, 'r+b')
        self.mmap_f = mmap.mmap(self.file_handle.fileno(), 0)

        class FileByteAccess(BaseByteAccess):

            """Read/write bytes to a file on disk."""

            def _read_bytes(slf, offset, size):
                begin = slf.offset + offset
                end = begin + size
                return self.mmap_f[begin:end]

            def _write_bytes(slf, offset, to_write):
                begin = slf.offset + offset
                end = begin + len(to_write)
                self.mmap_f[begin:end] = to_write

        self.ByteAccess = FileByteAccess

    def close(self):
        """Close the file and invalidate all child ByteAccesses."""
        self.mmap_f.close()
        self.file_handle.close()
