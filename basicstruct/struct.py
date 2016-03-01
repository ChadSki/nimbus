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

    """Wrap a ByteAccess and implement a struct interface.

    Attributes
    ----------
    byteaccess : ByteAccess
        The underlying data which a BasicStruct mediates access to.

    fields : Dict[str, BasicField]
        
    """

    def __init__(self, byteaccess, **fields):
        self.byteaccess = byteaccess
        self.fields = fields
        self.property_changed = Event()

    def __getattr__(self, attr_name):
        """Invoke a field, reading from the underlying data.
        
        This method is called when normal attribute lookup fails. It is here
        used to extend attribute lookup to the `fields` dictionary, so that
        those fields look like normal attributes."""
        if attr_name == 'fields':
            return self.__dict__['fields']
        elif attr_name in self.fields:
            try:
                return self.fields[attr_name].getf(self.byteaccess)
            except KeyError as err:
                raise AttributeError(
                    ("Attribute name `{}` does not appear to be a member"
                     "of this struct").format(attr_name)) from err
        else:
            return self.__dict__[attr_name]

    def __setattr__(self, attr_name, newvalue):
        """Invoke a field, writing to the underlying data.

        If the field has changed, invokes the `property_changed` event handler
        and triggers any registered events.
        
        This method is called when normal attribute lookup fails. It is here
        used to extend attribute lookup to the `fields` dictionary, so that
        those fields look like normal attributes."""
        fields = {}
        try:
            fields = self.fields
        except KeyError:
            pass

        if attr_name in fields:
            oldvalue = fields[attr_name].getf(self.byteaccess)
            if oldvalue != newvalue:
                fields[attr_name].setf(self.byteaccess, newvalue)
                self.property_changed(attr_name)
        else:
            self.__dict__[attr_name] = newvalue

def define_basic_struct(struct_size, **fields):
    """Returns a constructor function for a newly defined struct.

    Parameters
    ----------
    struct_size : int
        size of the struct in bytes

    **fields : Dict[str, BasicField]
        the remaining arguments are grouped into a dictionary, with the
        argument name as the key and the argument itself (which should be a
        BasicField) as the value.
    """
    def finish_construction(thing_access, offset):
        # enclose the bytes we need
        byteaccess = thing_access(offset, struct_size)
        # build the struct interface around it
        return BasicStruct(byteaccess, **fields)
    return finish_construction
