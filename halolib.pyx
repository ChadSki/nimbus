# cython: language_level=3
import xml.etree.cElementTree as et
from functools import partial
from copy import deepcopy

def make_property(field):
    if 'description' in field.attrib:
        doc = field.attrib['description']
    else:
        doc = field.attrib['name'].replace('_', ' ')

    def fget(self):
        return self.buffer

    def fset(self, value):
        self.buffer = value

    def fdel(self):
        del self._foo

    return property(fget, fset, fdel, doc)

def make_class(xml_filepath):
    base_struct = et.parse(xml_filepath).getroot()

    # define class using a dynamic name
    new_class = type(base_struct.attrib['name'], (object,), {'buffer': None})

    # roundabout way of defining a constructor
    new_class.__init__ = (lambda self, buffer: setattr(new_class, 'buffer', buffer))

    # define properties based on XML
    for field in base_struct:
        setattr(new_class, field.attrib['name'], make_property(field))

    return new_class
