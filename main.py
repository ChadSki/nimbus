from halolib import load_map_from_file

halomap = load_map_from_file('bloodgulch.map')

print(halomap)

for tag in halomap.tags:
    print(tag)

halomap.close()
