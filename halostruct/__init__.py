from fields import field

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

IndexHeader = \
    BasicStruct("IndexHeader",
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


MyStruct = \
    BasicStruct("MyStruct",
        foo=field.Asciiz(offset=0, maxlength=32),
        bar=field.Ascii(offset=32, length=4),
        baz=field.Int16(offset=36),
        qux=field.Int16(offset=38))

MyStruct2 = \
    HaloStruct("MyStruct2",
        halomap=None,
        foo=field.Asciiz(offset=0, maxlength=32),
        bar=field.Ascii(offset=32, length=4),
        baz=field.Int16(offset=36),
        qux=field.Int16(offset=38),
        fiz=halofield.TagReference(offset=40, loneid=True),
        buz=halofield.StructArray(offset=44, struct_type=BasicStruct("BuzStruct",
            buz_num=field.Int16(offset=0),
            buz_size=field.Int16(offset=0))))
