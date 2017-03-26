#!/usr/bin/env python

from __future__ import print_function
from evgen.core import SessionTemplate, GenericEventTemplate
from evgen.writers import GenericWriter
from evgen.formats import CSVEventFormat, JSONEventFormat

# same events will be sent to different sinks using different formats

class CustomWriter1(GenericWriter):
    def send(self, event):
        print("JSON:", self.Format.format(event))
    
class CustomWriter2(GenericWriter):
    def send(self, event):
        print("CSV:",self.Format.format(event))

session = SessionTemplate()
csv_format = CSVEventFormat()
json_format = JSONEventFormat()

json_conn = CustomWriter1(format=json_format)
csv_conn = CustomWriter2(format=csv_format)

start_event = GenericEventTemplate("START")

stop_event = GenericEventTemplate("STOP")

"""
You may add writers to all events individually, like that:

start_event.add_writer(json_conn)
start_event.add_writer(csv_conn)
stop_event.add_writer(json_conn)
stop_event.add_writer(csv_conn)

But most often it is more convenient to define it for whole session:
"""

session.add_event(start_event,probability=1)
session.add_event(stop_event, probability=1)
session.add_writer(json_conn)
session.add_writer(csv_conn)
session.generate()

