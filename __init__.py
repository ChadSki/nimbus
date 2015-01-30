# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import set_fields_dir, set_plugins_dir
from halomap import load_map
import os


def main():
    halolib = os.path.join(os.environ['DROPBOX'],
                           r'Workbench\CodeProjects\HaloFiles\Source Code\Halolib')
    set_fields_dir(os.path.join(halolib, r'plugins\fields'))
    set_plugins_dir(os.path.join(halolib, r'converter\output'))
    m = load_map('./beavercreek.map')

    for tag in m.tags():
        repr(tag)

if __name__ == '__main__':
    main()
