from xmlplugins import load_plugin

def load_map_from_file(map_path):
    MapHeader = load_plugin('map_header.xml')
    IndexHeader = load_plugin('index_header.xml')
    IndexEntry = load_plugin('index_entry.xml')

    mapfile = open(map_path, 'r+b')
    map_bytes = bytes(mapfile.read())

    mh = MapHeader(map_bytes)
    print(mh, '\n')

    ih = IndexHeader(map_bytes, mh.index_offset)
    print (ih, '\n')

    for i in range(ih.tag_count):
        ie = IndexEntry(map_bytes, mh.index_offset + IndexHeader.struct_size + (i * IndexEntry.struct_size))
        print(ie.first_type[::-1])
    
load_map_from_file('beavercreek.map')