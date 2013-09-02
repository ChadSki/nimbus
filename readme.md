# halolib.py

halolib.py is a library  for Python 3 which provides scriptable editing of Halo mapfiles, either on disk or in Halo's memory.

halolib.py aims to be compatible with Halo 1 PC on Windows, and HaloMD on Mac OS X.

## Example usage

As an example of modding at runtime, here we swap the projectile of the player's starting weapon with a more powerful projectile

### mem_example.py
```python
from halolib import *
load_plugins('.\plugins')

halomap = load_map_from_memory(fix_video_render=True)

print(halomap)
for tag in halomap.get_tags('bipd'):
    first_weapon = tag.weapons[0].weapon

    print(tag)
    print('before swap:%s' % first_weapon.projectile)

    first_weapon.projectile = halomap.get_tag('proj', 'charged')

    print('after swap: %s\n' % first_weapon.projectile)

halomap.close()
```

### Output
```
[index_header]
    primary_magic: 1078198312
    base_tag_ident: 3782475776
    map_id: 1579874334
    tag_count: 2408
    verticie_count: 447
    verticie_offset: 1519616
    indicie_count: 447
    indicie_offset: 6864260
    model_data_length: 7203188
    integrity: tags

[bipd]characters\cyborg_mp\cyborg_mp(3792109715)
before swap:[proj]weapons\assault rifle\bullet(3802071339)
after swap: [proj]weapons\plasma rifle\charged bolt(3883664904)

[bipd]characters\cyborg\cyborg(3904440133)
before swap:[proj]weapons\plasma rifle\charged bolt(3883664904)
after swap: [proj]weapons\plasma rifle\charged bolt(3883664904)
```

## Community

- www.opencarnage.net
- www.macgamingmods.com/forums
- www.modhalo.net
- www.halomods.com
