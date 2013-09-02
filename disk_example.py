from halolib import *
load_plugins('.\plugins')

halomap = load_map_from_file('beavercreek.map')

print(halomap)
for tag in halomap.get_tags('weap'):
    print(tag.layout)

halomap.close()
