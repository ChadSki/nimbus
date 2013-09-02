from halolib import *
load_plugins('.\plugins')
m = load_map_from_memory(fix_video_render=True)


ass_rifle = m.get_tag('weap', 'ass')
pistol = m.get_tag('weap', '\\pistol')
charged = m.get_tag('proj', 'charged')
rocket = m.get_tag('proj', 'rocket')

ass_rifle.triggers[0].projectile = charged
pistol.triggers[0].projectile = m.get_tag('vehi', 'banshee')

