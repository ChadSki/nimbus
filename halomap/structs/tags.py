# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from basicstruct import field
from .halostruct import define_halo_struct


tag_types = {}
# type: Dict[str, HaloMapStruct]

tag_types['weap'] = define_halo_struct(
    primary_magic=field.UInt32(offset=0),
    base_tag_ident=field.UInt32(offset=4),
    map_id=field.UInt32(offset=8),
    tag_count=field.UInt32(offset=12),
    verticie_count=field.UInt32(offset=16),
    verticie_offset=field.UInt32(offset=20),
    indicie_count=field.UInt32(offset=24),
    indicie_offset=field.UInt32(offset=28),
    model_data_length=field.UInt32(offset=32),
    integrity=field.Ascii(offset=36, length=4, reverse=True))
