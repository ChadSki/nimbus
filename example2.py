from halolib import *
load_plugins('.\plugins')

halomap = load_map_from_memory(video_render=False)

print(halomap)
for tag in halomap.tags:
    if tag.first_class == 'bipd':
        print(tag)
        print('before:%f' % tag.jump_velocity)
        tag.jump_velocity *= 8
        print('after:%f\n' % tag.jump_velocity)

halomap.close()