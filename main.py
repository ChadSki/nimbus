import halolib

halolib.load_plugins('.\plugins')

halomap = halolib.load_map_from_file('bloodgulch.map')

print(halomap)
for tag in halomap.tags:
    if tag.first_class == 'bipd':
        print(tag)
        print('    turn speed: %f\n' %tag.turn_speed)

halomap.close()
