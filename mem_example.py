# Welcome to Nimbus! If you just ran develop.cmd and are viewing this in the
# IDLE editor, press F5 to run this example. Halo must be running in the background.

import nimbus
map = nimbus.HaloMap.from_memory()

# weapons
pistol = map.tag('weap', '\\pistol')
rifle = map.tag('weap', 'assault rifle')
banshee_gun = map.tag('weap', 'banshee')

# vehicles
warthog = map.tag('vehi', 'warthog')

# projectiles
rocket = map.tag('proj', 'rocket')
plasma = map.tag('proj', 'plasma grenade')

# make edits
pistol.triggers[0].projectile = rocket        # pistol now shoots rockets
rifle.triggers[0].projectile = rocket         # assault rifle now shoots rockets
banshee_gun.triggers[0].projectile = warthog  # banshee primary trigger now spawns warthogs
banshee_gun.triggers[1].projectile = plasma   # banshee secondary trigger now shoots plasma grenades

print("Swaps complete! Try shooting the assault rifle, or the banshee gun.")
