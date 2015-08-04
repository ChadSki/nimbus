# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import abc


class Field(metaclass=abc.ABCMeta):

    """Abstract base class for fields in a struct.

    Fields are parented by a struct, which can be accessed via `self.parent`.

    The getf/setf functions translate between Python values and raw data
    contained in `self.parent.byteaccess`."""

    def __init__(self, *, offset, docstring, **kwargs):
        self.offset = offset
        self.docstring = docstring
        self.parent = None  # will be set by parent struct

    @abc.abstractmethod
    def getf(self):
        pass

    @abc.abstractmethod
    def setf(self, value):
        pass
