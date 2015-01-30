# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

from .notify import Event
from importlib import import_module
from os import path
import functools
import sys
import traceback
import xml.etree.ElementTree as et

fields_dir = '.'
plugins_dir = '.'


def set_fields_dir(directory):
    global fields_dir
    fields_dir = directory


def set_plugins_dir(directory):
    global plugins_dir
    plugins_dir = directory


def try_parse_int(s):
    """Parse integers from string according to the Entity plugin spec."""
    try:
        s = s.strip().lower()
        return int(s, 16) if s.startswith('0x') else int(s, 10)
    except ValueError:
        return s


def camel_case(s):
    """Convert snake_case to CamelCase."""
    return ''.join(x.title() for x in s.split('_'))


@functools.lru_cache()
def field_type(typename):
    """Import a field plugin and return its constructor.

    Field types are constantly reused, so this function is cached."""
    if fields_dir not in sys.path:
        sys.path.append(fields_dir)
    return import_module(typename).field


class ObservableStruct(object):

    def __init__(self, byteaccess, halomap):
            self.byteaccess = byteaccess
            self.halomap = halomap
            self.property_changed = Event()

    def __dir__(self):
            """A sorted list of methods and properties available to this class."""
            return sorted(self.field_names)
            # + ['byteaccess', 'field_names', 'halomap', 'property_changed'])

    def __repr__(self):
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
                    print('Error getting "{}" from "{}"'.format(name, self.class_name))
                    print(traceback.format_exc())

                except (ValueError):
                    raise

            r += '\n}'  # close JSON object
            return r


def struct_helper(layout):
    """Recursively define a new struct type based on the given xml definition."""
    try:
        # typename, e.g. "MagazineStruct" or "BipdStruct". Doesn't need to be unique.
        class_name = camel_case(layout.attrib['name']) + 'Struct'

        fields = {}  # {name => property}
        for node in layout:
            try:
                answer = field_type(typename=node.tag)(

                    # if a field involves another struct, load that too (recurse)
                    struct_class=(struct_helper(node)
                                  if node.tag == 'struct_array' else
                                  None),

                    # if present, load enum options from child nodes
                    options={
                        option.attrib['name']: try_parse_int(option.attrib['value'])
                        for option in node.iter('option')
                    },

                    # everything else (via xml attributes)
                    **{name: try_parse_int(value)
                       for name, value in node.attrib.items()})
                fields[node.attrib['name']] = answer

            except TypeError:
                print('Error while parsing <{}> node "{}"'.format(node.tag,
                                                                  node.attrib['name']))
                for key in node.attrib:
                    print('    {} => {}'.format(key, node.attrib[key]))
                raise

            except (ImportError, NotImplementedError):
                print('Skipping import of "{}" type'.format(node.tag))
                if 'int' in node.tag:
                    raise

        # build struct type
        return type(class_name, (ObservableStruct,), dict(
                    struct_size=int(layout.attrib['size'], 0),
                    class_name=class_name,
                    field_names=sorted(name for name in fields),
                    **fields))

    except:
        print('Error while parsing <{}> node "{}"'.format(layout.tag,
                                                          layout.attrib['name']))
        raise


@functools.lru_cache()
def struct_type(name):
    """Open a struct definition from an xml plugin file.

    This function is cached so that plugins do not have to be reloaded each time
    the same type is encountered."""

    try:
        # Find and open the plugin
        filepath = path.join(plugins_dir, name + '.xml')
        root_node = et.parse(filepath).getroot()

        if name != root_node.attrib['name']:
            print(
                'Plugin "{}" file name does not match struct name {}'.format(
                    filepath, root_node.attrib['name']))

        # Define a new class based on the XML definition
        return struct_helper(root_node)

    except:
        print('Error while parsing {}: '.format(filepath))
        raise
