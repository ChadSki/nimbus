# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from plugins import struct_type


class HaloTag(object):

    """Encapsulates an index entry, tag name, and metadata."""

    def __init__(self, index_entry, name_access, meta_access, halomap):
        # these attributes are all protected from erroneous assignment
        #object.__setattr__(self, 'name_field', field_type('asciiz'))
        object.__setattr__(self, 'index_entry', index_entry)
        object.__setattr__(self, 'meta_access', meta_access)
        object.__setattr__(self, '_meta', None)
        object.__setattr__(self, 'halomap', halomap)

    @property
    def name(self):
        return 'Foo'  # self.name_field.Value

    @name.setter
    def name(self, value):
        pass  # self.name_field.Value = value

    @property
    def meta(self):
        if self._meta is None:
            self._meta = struct_type(self.index_entry.first_class)(
                self.meta_access, self.halomap)
        return self._meta

    @meta.setter
    def meta(self, value):
        raise Exception('Replacing entire meta at once not yet implemented.')

    def __str__(self):
        """Returns a 1-line string representation of this tag."""
        return '[{}]{}({})'.format(self.index_entry.first_class,
                                   self.name,
                                   self.index_entry.ident)

    def __repr__(self):
        """Returns a full string representation of this tag and its metadata."""
        return str(self) + str(self.meta)

#    def __getattr__(self, name):
#        """Allow direct access of attributes from self.index_entry and self.meta.
#
#        Getting an attribute resolves in the following order:
#            1. First self's attributes are checked (happens implicitly)
#            2. If nothing was found, this method is invoked. Check self.index_entry
#            3. If nothing was found, check self.meta
#            4. If checking self.meta fails just let the AttributeError propagate upwards
#        """
#        try:
#            return getattr(self.index_entry, name)
#        except AttributeError:
#            return getattr(self.meta, name)
#
#    def __setattr__(self, name, value):
#        """Allow direct access of attributes from self.index_entry and self.meta.
#
#        Setting an attribute resolves in the following order:
#            1. [list of attributes] are exempt from being replaced
#            2. Other attributes in self can be assigned to
#            3. If the attribute is not found, check self.index_entry
#            4. If the attribute is not found, check self.meta
#            5. If checking self.meta fails, raise AttributeError
#        """
#        if name in ['meta', 'index_entry', 'name_field', 'meta_access', 'halomap']:
#            raise Exception('%s is protected from erroneous assignment.' % name)
#
#        elif name in self.__dict__:
#            object.__setattr__(self, name, value)
#
#        elif hasattr(self.index_entry, name):
#            setattr(self.index_entry, name, value)
#
#        elif hasattr(self.meta, name):
#            setattr(self.meta, name, value)
#
#        else:
#            raise AttributeError('Not allowed to create new attributes on HaloTag.')
