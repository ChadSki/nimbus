# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.
"""
Common interface for reading and writing binary data to files and processes.

Within a ByteAccess, offsets are relative. This means that ByteAccesses which
wrap the same data always appear and behave identically, regardless of where
that data actually is. This is useful when operations need to be performed on
identical data from different locations.

Example usage:

    import byteaccess

    if location == 'file':
        data_context = byteaccess.FileContext('file.txt')
    elif location == 'mem'
        data_context = byteaccess.WinMemContext('process.exe')

    foo = data_context.ByteAccess(offset, size)
    foo.write_bytes(0, b'somedata')
    foo.read_bytes(4, 4)  #=> b'data'
"""

__version__ = '0.3.0'
__all__ = ['FileContext', 'MemContext']

from .filecontext import FileContext
import platform


p = platform.system()
if p == 'Windows':
    from .winmemcontext import WinMemContext
    MemContext = WinMemContext

elif p == 'Darwin':
    raise NotImplementedError("Mac support not yet available")

else:
    raise NotImplementedError("Unsupported platform.")
