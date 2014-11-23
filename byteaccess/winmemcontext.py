# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .basebyteaccess import BaseByteAccess
from .windowsinterop import find_process
from ctypes import (byref, c_ulong, c_char_p, create_string_buffer, windll)
k32 = windll.kernel32


class WinMemContext(object):

    """Context for creating ByteAccesses which read and write to a Windows process.

    Usage:
        context = WinMemContext('notepad')
        context.ByteAccess(offset, size)
    """

    def __init__(self, process_name):
        """Instantiate a WinMemContext for a specific process.

        process_name -- The name of the target process. e.g. 'notepad' or 'notepad.exe'
        """
        if not '.' in process_name:
            process_name += '.exe'

        PROCESS_ALL_ACCESS = 0x1F0FFF
        process_entry = find_process(process_name.encode('ascii'))
        self.process = k32.OpenProcess(PROCESS_ALL_ACCESS, False,
                                       process_entry.th32ProcessID)

        class WinMemByteAccess(BaseByteAccess):

            """Read/write bytes to a specific process's memory."""

            def _read_bytes(slf, offset, size):
                address = slf.offset + offset
                buf = create_string_buffer(size)
                bytesRead = c_ulong(0)
                if k32.ReadProcessMemory(self.process, address,
                                         buf, size, byref(bytesRead)):
                    return bytes(buf)
                else:
                    raise RuntimeError("Failed to read memory")

            def _write_bytes(slf, offset, to_write):
                address = slf.offset + offset
                buf = c_char_p(to_write)
                size = len(to_write)
                bytesWritten = c_ulong(0)
                if k32.WriteProcessMemory(self.process, address,
                                          buf, size, byref(bytesWritten)):
                    return  # Success!
                else:
                    raise RuntimeError("Failed to write memory")

        self.ByteAccess = WinMemByteAccess

    def close(self):
        """Close the process and invalidate all child ByteAccesses."""
        k32.CloseHandle(self.process)
