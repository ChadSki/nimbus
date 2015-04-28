# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import functools
import os
import traceback
import xml.etree.ElementTree as ElementTree
from .fields import field_type
from .event import Event


class ObservableStruct(object):

    """TODO

    Does __init__ get documented here?
    """

    def __init__(self, byteaccess, halomap):
            self.byteaccess = byteaccess
            self.halomap = halomap
            self.collection_changed = Event()

    def __dir__(self):
            """A sorted list of methods and properties available to this class."""
            return sorted(self.field_names)
            # + ['byteaccess', 'field_names', 'halomap', 'property_changed'])

    def __repr__(self):
        return self.json()

    def json(self):
        """Generate a string representation of this struct in JSON format."""
        r = '{'                                      # open JSON object
        for name in self.__dir__():                  # for each field:
            r += '\n    "{0}": '.format(name)        # single-indented field name
            try:
                value = getattr(self, name)

                lines = str(value).split('\n')
                if len(lines) > 1:
                    r += lines.pop(0)  # attach the first part directly
                    for line in lines:
                        r += '\n    ' + line  # indent the remaining lines
                else:
                    if isinstance(value, bool):
                        r += str(value).lower()
                    elif isinstance(value, str):
                        r += repr(str(value)).replace(
                            '"', '@').replace(
                            "'", '"').replace(
                            '@', "'")
                    elif value is None:
                        r += 'null'
                    else:
                        r += str(value)
                r += ','  # comma to close this field

            except (AttributeError, RuntimeError):
                print('parse: error getting "{}" from "{}"'
                      .format(name, self.class_name))
                print(traceback.format_exc())

        r += '\n}'  # close JSON object
        return r


def pascal_case(s):
    """Convert snake_case to PascalCase."""
    return ''.join(x.title() for x in s.split('_'))


def try_parse_int(s):
    """Parse xml attributes according to the Entity plugin spec. If it looks
    like an integer, it's probably intended as an integer. Otherwise, a string.
    """
    try:
        s = s.strip().lower()
        return int(s, 16) if s.startswith('0x') else int(s, 10)
    except ValueError:
        return s


def _struct_type(struct_node):
    """Create a class representing a particular kind of struct. Recurse if this
    type of struct contains pointers to arrays of other structs (they need to be
    loaded before this one can be finished).

    Parameters
    ----------
    struct_node : ElementTree.Element
        A single struct from a plugin (possibly one of many).
    """
    try:
        # typename, e.g. "MagazineStruct" or "BipdStruct". Doesn't need to be unique.
        class_name = pascal_case(struct_node.attrib['name']) + 'Struct'

        fields = {}  # type: Dict[str, NotifyProperty]
        for field_node in struct_node:
            try:
                fields[field_node.attrib['name']] = field_type(typename=field_node.tag)(

                    # if a field involves another struct, load that too (recurse)
                    struct_class=(_struct_type(field_node)
                                  if field_node.tag == 'struct_array' else
                                  None),

                    # if present, load enum options from child field_nodes
                    options={
                        option.attrib['name']: try_parse_int(option.attrib['value'])
                        for option in field_node.iter('option')
                    },

                    # everything else (via xml attributes)
                    **{name: try_parse_int(value)
                       for name, value in field_node.attrib.items()})

            except TypeError:
                print('parse: error while parsing struct <{}> field "{}"'
                      .format(field_node.tag, field_node.attrib['name']))
                for key in field_node.attrib:
                    print('    {} => {}'.format(key, field_node.attrib[key]))
                raise

        # build and return the struct type
        return type(
            class_name, (ObservableStruct,),
            dict(
                class_name=class_name,
                struct_size=int(struct_node.attrib['size'], 0),
                field_names=sorted(name for name in fields),
                **fields))

    except:
        print('parse: error loading <{}> node "{}"'.format(struct_node.tag,
                                                           struct_node.attrib['name']))
        raise


plugins_dir = os.path.dirname(os.path.realpath(__file__))


@functools.lru_cache()
def struct_type(name):
    """Get the class for a specific struct type by name. Loads struct definitions from
    XML plugins in the struct directory. This function is cached so that plugins do not
    have to be reloaded each time the same type is encountered (which is often).

    Parameters
    ----------
    name : string
        todo
    """
    # Find and open the plugin
    filepath = os.path.join(plugins_dir, name + '.xml')
    root_node = ElementTree.parse(filepath).getroot()

    # Enforce matching names
    if name != root_node.attrib['name']:
        raise ValueError(
            'plugin "{}" filename does not match struct name "{}"'
            .format(filepath, root_node.attrib['name']))

    # Define a new class based on the XML definition
    return _struct_type(root_node)
