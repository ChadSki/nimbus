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


class NotifyProperty(property):

    """Triggers an event when the value is changed by a set operation."""

    def __init__(self, *args, fset, name, **kwargs):

        def newsetter(slf, newvalue):
            """Wrap the setter with a notification check"""
            oldvalue = slf.fget(slf)
            if oldvalue != newvalue:
                fset(slf, newvalue)
                slf.property_changed(self.name)

        super(NotifyProperty, self).__init__(*args, fset=newsetter, **kwargs)
        self.name = name
