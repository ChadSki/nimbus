# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from collections import MutableMapping
import functools
from os import path
import re
from xml.etree import ElementTree
from .fields import field_type
from .event import Event


def pascal_case(s):
    """Convert snake_case to PascalCase."""
    return ''.join(x.title() for x in s.split('_'))


def eschaton_int(s):
    """Parse integers the same way Eschaton does.

    By default, Python disagrees with Eschaton about leading zeroes. This logic
    fixes that; either this starts with 0x (and is hexadecimal), or it's a
    base-10 integer.
    """
    s = s.strip().lower()
    return int(s, 16) if s.startswith('0x') else int(s, 10)


def try_parse_int(s):
    """Parse xml attributes according to the Entity plugin spec. If it looks
    like an integer, it's probably intended as an integer. Otherwise, a string.
    """
    try:
        eschaton_int(s)
    except ValueError:
        return s


def load_fields(struct_node):
    fields = {}  # type: Dict[str, NotifyProperty]
    for field_node in struct_node:

        print('{} attrs:'.format(field_node.tag))
        for name, value in field_node.attrib.items():
            print("    {} = {}".format(name, value))
        try:
            kwargs = {name: try_parse_int(value)
                      for name, value in field_node.attrib.items()}

            # if a field involves another struct, load that type first
            if field_node.tag == 'struct_array':
                kwargs['struct_class'] = _struct_type(field_node)

            # load enum options if present
            options = {option.attrib['name']: try_parse_int(option.attrib['value'])
                       for option in field_node.iter('option')}

            if len(options) > 0:
                kwargs['options'] = options

            fields[field_node.attrib['name']] = \
                field_type(typename=field_node.tag)(**kwargs)

        except:
            print('error loading struct <{}> at field "{}"'
                  .format(struct_node.attrib['name'],
                          field_node.attrib['name']))
            print('field_node.attrib:')
            for key in field_node.attrib:
                print('    {} => {}'.format(key, field_node.attrib[key]))
            raise

    return fields


def _struct_type(struct_node):
    """Create a class representing a particular kind of struct. Recurse if this
    type of struct contains pointers to arrays of other structs (they need to be
    loaded before this one can be finished).

    Parameters
    ----------
    struct_node : ElementTree.Element
        A single struct from a plugin (possibly one of many).
    """
    class DynamicStruct(MutableMapping):

        """Dynamically implemented struct type, with reflection and mutability.

        This class knows about its own fields, and provides access to them by name.
        For example `foo.bar` in addition to the dictionary-style access `foo[bar]`
        both access the "bar" field as defined in XML plugins.

        TODO:
            - I want to implement 'observable' idiom in the future
        """
        store = load_fields(struct_node)  # type: Dict[str, ObservableField]
        struct_size = int(struct_node.attrib['struct_size'], 0)

#        @property
#        def store(self):
#            return DynamicStruct.store
#
#        @property
#        def struct_size(self):
#            return DynamicStruct.struct_size

        def fields(self, field_type, *name_fragments):
            """Filter fields by type and by name. Iterates through all fields which
            match the given criteria.

            Parameters
            ----------
            field_type : string
                Filter your search by type, or use the empty string to include all
                classes in your search. Regular expressions are enabled.

                Examples: '', 'int', '^int', 'asciiz?|rawdata'

            name_fragments : tuple of string, optional
                Each fragment is independently searched for in tag names. Only tags
                which contain all fragments will be returned. Regular expressions
                are enabled.

                Example fragments: '', 'cyborg', 'rifle|pistol'
            """
            def match(field):
                return (re.search(field_type, field.field_type)
                        and all(re.search(regex, field.name)
                                for regex in name_fragments))

            return filter(match, type(self).store.values())

        def __init__(self, halomap, offsets):
            self.byteaccess = halomap.context.ByteAccess(
                offsets[halomap.context.where],
                type(self).struct_size)
            self.halomap = halomap
            self.collection_changed = Event()

        def __getitem__(self, key):
            return self.store[self.__keytransform__(key)]

        def __setitem__(self, key, value):
            self.store[self.__keytransform__(key)] = value

        def __delitem__(self, key):
            del self.store[self.__keytransform__(key)]

        def __iter__(self):
            return iter(self.store)

        def __len__(self):
            return len(self.store)

        def __keytransform__(self, key):
            return key

        def __getattr__(self, name):
            """Using magic, merges the attributes of self.store.

            Resolves in the following order:
                1. First self's attributes are checked
                2. If nothing was found, Python will run __getattr__ and check
                   self.store's attributes
                4. If both fail, just let the AttributeError propagate upwards.
            """
            return self.store[name].value.fget(self)


    # typename, e.g. "MagazineStruct" or "BipdStruct". Doesn't need to be unique.
    DynamicStruct.__name__ = pascal_case(struct_node.attrib['name']) + 'Struct'
    return DynamicStruct


@functools.lru_cache()
def struct_type(name):
    """Get the class for a specific struct type by name. Loads struct definitions from
    XML plugins in the struct directory. This function is cached so that plugins do not
    have to be reloaded each time the same type is encountered (which is often).

    Parameters
    ----------
    name : string
        Name of the struct type to load (snake_case)
    """
    # Find and open the plugin
    this_dir = path.dirname(path.realpath(__file__))
    plugins_dir = path.join(this_dir, "structs")
    filepath = path.join(plugins_dir, name + '.xml')
    root_node = ElementTree.parse(filepath).getroot()

    # Enforce matching names
    if name != root_node.attrib['name']:
        raise ValueError(
            'plugin "{}" filename does not match struct name "{}"'
            .format(filepath, root_node.attrib['name']))

    # Define a new class based on the XML definition
    try:
        return _struct_type(root_node)
    except:
        print('\nerror in plugin "{}"\n'.format(filepath))
        raise
