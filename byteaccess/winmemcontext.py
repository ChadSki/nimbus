# Copyright (c) 2015, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .basebyteaccess import BaseByteAccess
from .windowsinterop import find_process
import ctypes
from ctypes import (c_ulong, c_char_p)
k32 = ctypes.windll.kernel32


class WinMemContext(object):

    """Context for creating ByteAccesses which read and write to a Windows process.

    Usage:
        context = WinMemContext('notepad')
        foo = context.ByteAccess(offset, size)
        bar = context.ByteAccess(other_offset, other_size)
    """

    def __init__(self, process_name):
        """Instantiate a WinMemContext for a specific process.

        process_name -- The name of the target process. e.g. 'notepad' or 'notepad.exe'
        """
        if '.' not in process_name:
            process_name += '.exe'

        PROCESS_ALL_ACCESS = 0x1F0FFF
        process_entry = find_process(process_name.encode('ascii'))
        self.process = k32.OpenProcess(PROCESS_ALL_ACCESS, False,
                                       process_entry.th32ProcessID)

        # Define a ByteAccess specific to this process
        class WinMemByteAccess(BaseByteAccess):

            """Read/write bytes to a specific process's memory."""

            def _read_bytes(slf, offset, size):
                address = slf.offset + offset
                buf = ctypes.create_string_buffer(size)
                bytesRead = c_ulong(0)
                if k32.ReadProcessMemory(self.process, address, buf, size,
                                         ctypes.byref(bytesRead)):
                    return bytes(buf)
                else:
                    raise OSError("Failed to read memory. " +
                                  "offset:{0} size:{1}"
                                  .format(offset, size))

            def _write_bytes(slf, offset, to_write):
                address = slf.offset + offset
                buf = c_char_p(to_write)
                size = len(to_write)
                bytesWritten = c_ulong(0)
                if k32.WriteProcessMemory(self.process, address, buf, size,
                                          ctypes.byref(bytesWritten)):
                    return  # Success!
                else:
                    raise OSError("Failed to write memory. " +
                                  "offset:{0} size:{1}"
                                  .format(offset, size))

        # store under a common name, so we can find without knowing the specific implementation
        self.ByteAccess = WinMemByteAccess

    def close(self):
        """Close the process and invalidate all child ByteAccesses."""
        k32.CloseHandle(self.process)
