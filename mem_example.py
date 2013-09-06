from halolib import *
load_plugins('.\plugins')
m = load_map_from_memory(fix_video_render=True)

# weaps
rifle = m.get_tag('weap', 'assault rifle')
pistol = m.get_tag('weap', '\\pistol')
banshee_gun = m.get_tag('weap', 'banshee')

# vehis
banshee = m.get_tag('vehi', 'banshee')

# projs
rocket = m.get_tag('proj', 'rocket')
plasma = m.get_tag('proj', 'plasma grenade')
plasma.initial_velocity = 0.2
plasma.final_velocity = 0.2

# do swaps
rifle.triggers[0].projectile = rocket           # assault rifle shoots rockets
banshee_gun.triggers[0].projectile = warthog    # banshee primary trigger spawns warthogs
banshee_gun.triggers[1].projectile = plasma     # banshee secondary trigger shoots plasma grenades

#banshee_gun.triggers[0].projectile = rocket
#banshee_gun.triggers[1].projectile = m.get_tag('vehi', 'scorpion')
