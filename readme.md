# halolib.py

halolib.py is a library  for Python 3 which provides scriptable editing of Halo mapfiles, either on disk or in Halo's memory.

halolib.py aims to be compatible with Halo 1 PC on Windows, and HaloMD on Mac OS X.

## Example usage

Here we selectively display the (partial) layout of a Halo tag. Layouts are defined in xml plugins, and will become more complete in the future!

### example.py
```python
from halolib import *
load_plugins('.\plugins')

halomap = load_map_from_file('beavercreek.map')

print(halomap)
for tag in halomap.tags:
    if tag.first_class == 'bipd':
        print(tag)

halomap.close()
```

### Output
```
[map_header]
  integrity: head
  game_version: 7
  map_struct_size: 13523732
  offset12: b'\x00\x00\x00\x00'
  index_offset: 8042316
  metadata_length: 5481416
  offset24: b'\x00\x00\x00\x00\x00\x00\x00\x00'
  map_name: beavercreek
  map_build: 01.00.00.0564
  map_type: 0

[index_header]
  primary_magic: 1078198312
  base_tag_ident: 3782475776
  map_id: 1968773264
  tag_count: 2353
  verticie_count: 429
  verticie_offset: 872448
  indicie_count: 429
  indicie_offset: 6832776
  model_data_length: 7169868
  integrity: tags

[bipd]characters\cyborg_mp\cyborg_mp
[bipd]characters\cyborg\cyborg
```

## Community

- www.opencarnage.net
- www.macgamingmods.com/forums
- www.modhalo.net
- www.halomods.com
