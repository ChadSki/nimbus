# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from collections import OrderedDict
from collections.abc import MutableMapping


class ObservableDict(MutableMapping):

    def __init__(self):
        self.store = OrderedDict()
