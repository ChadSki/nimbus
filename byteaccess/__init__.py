# Copyright (c) 2015, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.
"""
Common interface for reading and writing binary data to files and processes.

Within a ByteAccess, offsets are relative. This means that ByteAccesses which
wrap the same data always appear and behave identically, regardless of where
that data actually is. This is useful when operations need to be performed on
identical data from different locations in the same source, or from different
sources altogether.

Example usage:

    import byteaccess

    if location == 'file':
        data_context = byteaccess.FileContext('filename.txt')
    elif location == 'mem'
        data_context = byteaccess.MemContext('processname')

    foo = data_context.ByteAccess(offset, size)

    foo.write_bytes(0, b'somedata')    # write data to offsets within the ByteAccess

    foo.read_bytes(2, 6)  #=> b'medata'  # read any length of data from any offset
"""

__version__ = '0.4.0'
__all__ = ['FileContext', 'MemContext']


from .filecontext import FileContext  # FileContext is the same on all platforms

import platform
p = platform.system()  # MemContext is platform dependent
if p == 'Windows':
    from .winmemcontext import WinMemContext
    MemContext = WinMemContext

elif p == 'Darwin':
    raise NotImplementedError("Mac support not yet available")
    #from .macmemcontext import MacMemContext
    #MemContext = MacMemContext

else:
    raise NotImplementedError("Unsupported platform.")
