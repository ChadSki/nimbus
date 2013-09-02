from halolib import *
load_plugins('.\plugins')

halomap = load_map_from_file('beavercreek.map')

print(halomap)
for tag in halomap.tags:
    if tag.first_class == 'bipd':
        print(tag.layout)

halomap.close()
