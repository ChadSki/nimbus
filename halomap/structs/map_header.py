# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from basicstruct.struct import BasicStruct
from basicstruct import field

MapHeader = \
    BasicStruct("MapHeader",
        integrity=field.Ascii(offset=0, length=4, reverse=True),
        game_version=field.UInt32(offset=4),
        map_size=field.UInt32(offset=4),
        index_offset=field.UInt32(offset=16),
        metadata_size=field.UInt32(offset=20),
        map_name=field.Asciiz(offset=32, maxlength=32),
        map_build=field.Asciiz(offset=64, maxlength=64),
        map_type=field.UInt32(offset=128))