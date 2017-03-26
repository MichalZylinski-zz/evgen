#!/usr/bin/env python

from evgen.core import SessionTemplate, EventGroup, GenericEventTemplate
from evgen.writers import ConsoleWriter
from evgen.formats import CSVEventFormat
from random import uniform

#Random time series generator example

#creating custom event template
class TemperatureEventTemplate(GenericEventTemplate):
    def __init__(self, *args, **kwargs):
        GenericEventTemplate.__init__(self, *args, **kwargs)
        self.set_attribute('Temp', self.get_temp)

    def get_temp(self):
        temp_state = self.Session.Attributes.get('TempState')
        current_temp = temp_state + 1
        self.Session.set_attribute('TempState', current_temp)
        return current_temp 


eg = EventGroup()

event_format = CSVEventFormat(fields=["TimeStamp", "SessionId", "Temp"], sep=" ")
eg.add_event(TemperatureEventTemplate(writer=ConsoleWriter(format=event_format)), probability=1,delay=1000)

eg.set_repeat_policy(min=10, max=10)

session = SessionTemplate()
session.add_event_group(eg)
session.set_attribute('TempState', 20)
session.generate()