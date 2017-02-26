from evgen.core import UserProfile, UserTemplate, SessionTemplate
from evgen.events import GenericEventTemplate, EventGroup
from evgen.writers import DirectoryWriter

#if directory below doesn't exist it will be created
writer= DirectoryWriter("output")
#creating session with 20 generic events
eg = EventGroup()
eg.add_event(GenericEventTemplate(writer=writer), probability=1,delay=1000)
eg.set_repeat_policy(min=20, max=20)
session = SessionTemplate()
session.add_event_group(eg)

#following 2 lines should generate 2 separate files
session.generate()
session.generate()

#following profile should generate 10 separate files
user_profile = UserProfile("michal")

import datetime 

start = datetime.datetime.strptime("2015-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime("2015-10-31 23:59:00", "%Y-%m-%d %H:%M:%S")

user = UserTemplate(user_profile, number_of_sessions=10, start_date=start, end_date=end)
user.add_session(session)
user.generate(sorted=False)
