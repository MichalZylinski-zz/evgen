#!/usr/bin/env python

from evgen.core import SessionTemplate, GenericEventTemplate
from evgen.writers import ConsoleWriter

#basic 2-event example

session = SessionTemplate()
session.add_event(GenericEventTemplate("start"), probability = 1, delay=5000)
session.add_event(GenericEventTemplate("stop"), probability = 1)
session.add_writer(ConsoleWriter())
session.generate()