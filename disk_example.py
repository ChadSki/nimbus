import halolib
m = halolib.load_map("D:\\Program Files (x86)\\Microsoft Games\\Halo\\MAPS\\bloodgulch.map")

print(repr(m))

#def print_data(x):
#    print(x.struct_data)
#    for key in x.reflexives:
#        for each in x.reflexives[key]:
#            print_data(each)
#
#print_data(t.meta.export())

banshee = m.get_tag('vehi', 'banshee_mp')
warthog = m.get_tag('vehi', '\\warthog')

print(repr(banshee))
print(repr(warthog))

m.close()
