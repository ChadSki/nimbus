from halolib import *
load_plugins('.\plugins')

halomap = load_map_from_memory(fix_video_render=True)

print(halomap)
for tag in halomap.tags:
    if tag.first_class == 'bipd':
        first_weapon = tag.weapons[0].weapon

        print(tag)
        print('before swap:%s' % first_weapon.projectile)

        first_weapon.projectile = get_tag(halomap, 'proj', 'charged')

        print('after swap: %s\n' % first_weapon.projectile)

halomap.close()