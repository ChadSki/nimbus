import halolib
halolib.load_plugins('.\plugins')
m = halolib.load_map_from_file('beavercreek.map')

print(m)
for tag in m.get_tags('weap'):
    print(tag.layout)

m.close()
