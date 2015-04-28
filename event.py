# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.


class Event(set):

    """Used to run functions when certain conditions are met.

    When an event is triggered, it calls each of its handlers with the same
    arguments it was.
    """

    def __call__(self, *args, **kwargs):
        """Pass these arguments to each handler, in turn."""
        for each in self:
            each(*args, **kwargs)
