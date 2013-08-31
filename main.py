import halolib

halolib.load_plugins('.\plugins')

halomap = halolib.load_map_from_file('beavercreek.map')

print(halomap)
for tag in halomap.tags:
    if tag.first_class in halolib.halo_struct_classes:
        print(tag.layout_str)
    else:
        print(tag)

halomap.close()
