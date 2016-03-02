# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.
"""TODO"""

from basicstruct import field
from halolib.structs.halostruct import define_halo_struct
from halolib.structs import halofield


tag_types = {}
# type: Dict[str, HaloMapStruct]

tag_types['weap'] = define_halo_struct(struct_size=0x504,
    model=halofield.TagReference(offset=0x28),
    animation=halofield.TagReference(offset=0x38),
    collision=halofield.TagReference(offset=0x70),
    physics=halofield.TagReference(offset=0x80),
    )
