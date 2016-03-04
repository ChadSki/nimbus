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

tag_types['proj'] = define_halo_struct(struct_size=0x248,
    model=halofield.TagReference(offset=0x28),
    animation=halofield.TagReference(offset=0x38),
    collision=halofield.TagReference(offset=0x70),
    physics=halofield.TagReference(offset=0x80),
    initial_velocity=field.Float32(offset=0x1E4),
    final_velocity=field.Float32(offset=0x1E8),
    )

tag_types['effe'] = define_halo_struct(struct_size=0x700,
    events=halofield.StructArray(offset=0x34, struct_size=68,
        parts=halofield.StructArray(offset=0x2C, struct_size=104,
            spawned_object=halofield.TagReference(offset=0x18))))


tag_types['vehi'] = define_halo_struct(struct_size=0x3F0,
    model=halofield.TagReference(offset=0x28),
    animation=halofield.TagReference(offset=0x38),
    collision=halofield.TagReference(offset=0x70),
    physics=halofield.TagReference(offset=0x80),
    max_forward_velocity=field.Float32(offset=0x2F8),
    max_reverse_velocity=field.Float32(offset=0x2FC),
    acceleration=field.Float32(offset=0x300),
    deceleration=field.Float32(offset=0x304),
    )

tag_types['weap'] = define_halo_struct(struct_size=0x504,
    model=halofield.TagReference(offset=0x28),
    animation=halofield.TagReference(offset=0x38),
    collision=halofield.TagReference(offset=0x70),
    physics=halofield.TagReference(offset=0x80),
    )
