#!/usr/bin/env python

from evgen.core import SessionOwnerTemplate, SessionTemplate, GenericEventTemplate, EventGroup
from evgen.writers import DirectoryWriter

#if directory below doesn't exist it will be created
writer= DirectoryWriter("output")
#creating session with 20 generic events
eg = EventGroup()
eg.add_event(GenericEventTemplate(writer=writer), probability=1,delay=1000)
eg.set_repeat_policy(min=20, max=20)
session = SessionTemplate()
session.add_event_group(eg)


#following profile should generate 10 separate files in /output directory

import datetime 

start = datetime.datetime.strptime("2015-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime("2015-10-31 23:59:00", "%Y-%m-%d %H:%M:%S")

user = SessionOwnerTemplate("michalz")
user.set_number_of_sessions(10)
user.set_start_date(start)
user.set_end_date(end)
user.add_session(session)
user.generate()
