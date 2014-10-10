# Copyright (c) 2013, Chad Zawistowski
# All rights reserved.
#
# This software is free and open source, released under the 2-clause BSD
# license as detailed in the LICENSE file.

import pyevent
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs

class PyNotifyPropertyChanged(INotifyPropertyChanged):
    PropertyChanged, _propertyChangedCaller  = pyevent.make_event()

    def __init__(self):
        self.PropertyChanged, self._propertyChangedCaller = pyevent.make_event()

    def add_PropertyChanged(self, value):
        self.PropertyChanged += value

    def remove_PropertyChanged(self, value):
        self.PropertyChanged -= value

    def OnPropertyChanged(self, propertyName):
        if self.PropertyChanged is not None:
            self._propertyChangedCaller(self, PropertyChangedEventArgs(propertyName))


def notify_property(name):
    """Works just like a regular property, but additionally triggers the host
    class's OnPropertyChanged event when the value is changed.

    Saves the name of the property for each individual property-derived class; a new
    NotifyProperty class is generated for each name.
    """
    class NotifyProperty(property):
        def __init__(self, fget=None, fset=None, fdel=None, doc=None):
            super(NotifyProperty, self).__init__(
                fget=fget, fset=fset, fdel=fdel, doc=doc)

        def setter(self, fset):
            def newsetter(slf, newvalue):
                oldvalue = self.fget(slf)
                if oldvalue != newvalue:
                    fset(slf, newvalue)
                    slf.OnPropertyChanged(fset.__name__)
            return NotifyProperty(
                fget=self.fget, fset=newsetter, fdel=self.fdel, doc=self.__doc__)

    return NotifyProperty
