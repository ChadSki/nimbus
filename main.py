from halolib import make_class

def load_map_from_file(map_path):
    MapHeader = make_class('map_header.xml')
    IndexHeader = make_class('index_header.xml')
    IndexEntry = make_class('index_entry.xml')

    mh = MapHeader("stuff")

    print('\n', type(mh))
    for key in MapHeader.__dict__:
        if key[0] != '_':
            x = getattr(mh, key)
            print(key, x)
            setattr(mh, key, x + '1')


load_map_from_file('bloodgulch.map')