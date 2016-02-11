# Copyright (c) 2016, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

class Event(set):

    """A very simple event handler.
    
    Add an event handler (a function) with += and -= syntax.
    You may remove all handlers at once with `.clear()`.
    Invoke the handler with function call syntax `()`.
    
    Event handlers should be short and return quickly! Execution cannot
    continue until all event handlers have finished, so make it snappy."""

    def __call__(self, *args, **kwargs):
        for handler in self:
            handler(*args, **kwargs)


class BasicStruct(object):

    """TODO"""

    def __init__(self, **kwargs):
        self.fields = kwargs
        self.property_changed = Event()

    def __getattr__(self, attr_name):
        """Invoke a field, reading from the underlying data.
        
        This method is called when normal attribute lookup fails. It is here
        used to extend attribute lookup to the `fields` dictionary, so that
        those fields look like normal attributes."""
        try:
            return self.fields[attr_name].getf()
        except KeyError as err:
            raise AttributeError(
                ("Attribute name `{}` does not appear to be a member"
                 "of this struct").format(attr_name)) from err

    def __setattr__(self, attr_name, newvalue):
        """Invoke a field, writing to the underlying data.

        If the field has changed, invokes the `property_changed` event handler
        and triggers any registered events.
        
        This method is called when normal attribute lookup fails. It is here
        used to extend attribute lookup to the `fields` dictionary, so that
        those fields look like normal attributes."""
        oldvalue = self.fields[attr_name].getf()
        if oldvalue != newvalue:
            self.fields[attr_name].setf(newvalue)
            self.property_changed(attr_name)