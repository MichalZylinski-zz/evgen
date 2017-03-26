from __future__ import division
from builtins import range
from builtins import object
import datetime as dt
import uuid
from random import randrange, random, randint
from copy import copy
import user_agent
from faker import Faker
import types
from evgen.utils import *

faker = Faker()

class BaseTemplate(object):
    """
    BaseTemplate exposes static and dynamic properties through Attributes dictionary
    """
    def __init__(self):
        self.__attributes__ = {}

    def __getattr__(self, val):
        if val=="Attributes":
            attrs = {}
            #materializing dynamic properties and adding them to main dictionary
            for attr in self.__attributes__:
                if type(self.__attributes__[attr]) == types.NoneType: #skipping all attributes that are empty 
                        pass
                elif type(self.__attributes__[attr]) in [types.MethodType, types.FunctionType]:
                    try:
                        attrs[attr] = self.__attributes__[attr]()
                    except: #in case function relies on external object that has not been initialized yet
                        pass
                else:
                    attrs[attr] = self.__attributes__[attr]
            return attrs
        elif val in self.__attributes__: 
            if type(self.__attributes__[val]) in [types.MethodType, types.FunctionType]:
                return self.__attributes__[val]()
            else:
                return self.__attributes__[val]
        else:
            return object.__getattribute__(self, val)
            raise AttributeError("Property: %s does not exist" % val)

    def set_attribute(self, key, value):
        """
        Creates new static or dynamic attribute.
        """
        self.__attributes__[key] = value

    def update_attributes(self, dict):
        self.__attributes__.update(dict)

class GenericEventTemplate(BaseTemplate):
    def __init__(self, name=None, writer=None, **kwargs):
        BaseTemplate.__init__(self)
        self.set_attribute('Name',name)
        self.Name = name
        self.Session = None
        self.Owner = None
        self.update_attributes(kwargs)
        self.__writers__ = []
        if writer != None:
            self.add_writer(writer)

    def add_writer(self, writer,  replace=False):
        if replace:
            self.__writers__ = []
        if writer not in self.__writers__:
            self.__writers__.append(writer)

    def add_owner(self, owner):
        self.Owner = owner

    def add_session(self, session):
        self.Session = session
        self.update_attributes(session.Attributes)

    def generate(self):
        if len(self.__writers__) == 0:
            raise ValueError("Writer property missing.")
        for writer in self.__writers__:
            writer.send(self.Attributes)

class EventGroup(object):
    def __init__(self):
        self.Events = []
        self.min_repeat = 1
        self.max_repeat  = 1

    def add_event(self, event, probability, delay=1000, delay_random=0.1):
        self.Events.append((event, probability, delay, delay_random))

    def set_repeat_policy(self, min=1, max=1):
        self.min_repeat = min
        self.max_repeat = max

class SessionTemplate(BaseTemplate):
    def __init__(self, event_delay=1000, start_date=None,  session_delay=1000, session_random=0):
        BaseTemplate.__init__(self)
        self.Owner = None
        self.EventGroups = []
        self.__event_delay__ = event_delay
        self.__session_delay__ = dt.timedelta(milliseconds=session_delay)
        self.__sdr__ = session_random
        self.__writers__ = []
        if start_date is None: 
            start_date = dt.datetime.now()
        self.start_date = start_date
        self.last_session_end = self.start_date    

    def set_start_date(self, date):
        self.start_date = date

    def add_session_delay(self, time_delta):
        self.__session_delay__ = time_delta

    def add_event(self, event, probability, delay=None, delay_random=0.1):
        if delay is None:
            delay = self.__event_delay__
        #wrapping event onto single, basic EventGroup instance
        eg = EventGroup()
        eg.add_event(copy(event), probability, delay,delay_random)
        self.EventGroups.append(eg)
    
    def add_event_group(self, event_group):
        self.EventGroups.append(event_group)

    def add_owner(self, owner_template):
        self.Owner = owner_template

    def add_writer(self, writer):
        self.__writers__.append(writer)
     
    def generate(self, start_date=None):
        self.set_attribute("SessionId",  uuid.uuid4().hex)
        #initialize writers
        for eg in self.EventGroups:
            for e in eg.Events:
                e[0].add_session(self)
                for w in self.__writers__:
                    e[0].add_writer(w)

        if start_date:
            self.set_start_date(start_date)

        delay = 0
        session_events = []

        #owner attributes should remain the same for whole session:
        if self.Owner: 
            owner_attrs = self.Owner.Attributes

        #retrieving all static and dynamic user properties - they may change between sessions (i.e. IP)
        for eg in self.EventGroups:
            for i in range(randrange(eg.min_repeat, eg.max_repeat+1)):
                for e in eg.Events:
                    if random_test(e[1]):
                        timestamp = self.start_date+dt.timedelta(milliseconds=delay)
                        e[0].set_attribute("TimeStamp", timestamp)
                        #updating dictionary with UserProfile properties
                        if self.Owner:
                            e[0].update_attributes(owner_attrs)
                            e[0].add_owner(self.Owner)
                        e[0].generate()
                        if e[3]: #including random delay
                            i = randrange(-(e[2]*e[3]), (e[2]*e[3]))
                            delay += e[2]+i
                        else: 
                            delay += e[2]
                        self.last_session_end = e[0].TimeStamp

        #calculating next session delay
        if self.__sdr__:
            delay = self.__session_delay__.total_seconds()*1000
            sdelay = randrange(-delay*self.__sdr__, delay*self.__sdr__)
        else:
            sdelay = 0
        sdelay = dt.timedelta(milliseconds=self.__session_delay__.total_seconds()*1000+sdelay)
        self.last_session_end = self.last_session_end + sdelay
        self.start_date = self.last_session_end
        return self.start_date #returns next possible start date 

class SessionOwnerTemplate(BaseTemplate):
    def __init__(self, name=None):
        BaseTemplate.__init__(self)
        self.set_attribute('UserName', name)
        #uniform distributions by default
        self.h_dist = HourlyDistribution()
        self.m_dist = MonthlyDistribution()
        self.d_dist = WeeklyDistribution()
        self.sessions = []
        self.randomize_sessions = False
        self.s_dist = None #session distribution
        self.__nos__ = 0
        self.start_date = dt.datetime.now()
        self.end_date = self.start_date + dt.timedelta(days=30)
        self.session_dates = []

    def set_number_of_sessions(self, number_of_sessions, randomize=False):
        self.__nos__ = number_of_sessions
        self.randomize_sessions = randomize
    
    def set_start_date(self, date):
        """
        requires datetime.datetime object
        """
        self.start_date = date

    def set_end_date(self, date):
        self.end_date = date

    def add_hourly_distribution(self, distribution):
        self.h_dist = distribution

    def add_daily_distribution(self, distribution):
        self.d_dist = distribution

    def add_monthly_distribution(self, distribution):
        self.m_dist = distribution

    def add_session(self, session, delay=None):
        session.add_owner(self)
        self.sessions.append(session)

    def add_session_distribution(self, weights):
        self.s_dist = Distribution(sample_size=len(self.sessions), weights=weights)

    def __generate_random_date__(self):
        date_range = self.end_date-self.start_date
        years = list(range(self.start_date.year, self.end_date.year+1))
        while 1: #testing whether random date fits between start and end dates
            year = np.random.choice(years)
            if len(years) > 2:
                        month = self.m_dist.get_value()
            else: #if range is below one year
                month = self.m_dist.get_value(starts=self.start_date.month, ends=self.end_date.month)
            day = self.d_dist.get_value(year, month)
            hour = self.h_dist.get_value()
            min = randint(0,59)
            sec = randint(0,59)
            new_date =  dt.datetime(year=year, month=month, day=day, hour=hour, minute=min, second=sec)
            if self.start_date < new_date < self.end_date:
                break
        return new_date

    def generate(self):
        session_count = 0
        if self.s_dist is None:
            self.s_dist = Distribution(sample_size=len(self.sessions))
        begin = self.start_date
        while session_count < self.__nos__:
            if self.randomize_sessions:
                begin = self.__generate_random_date__()
            session = self.sessions[self.s_dist.get_value()]
            session.generate(start_date=begin)
            end = session.last_session_end 
            if self.randomize_sessions:                     
                if not self.__test_date_intersect__(begin, end) and end < self.end_date:
                    self.session_dates.append((begin,end))
            else:
                begin = end
            session_count += 1

    def __test_date_intersect__(self, begin, end):
        """
        Verify whether new session (described as beginning and end datetime object) overlaps with already existing ones.
        """
        for existing_start, existing_end in self.session_dates:
            if (existing_start < begin <existing_end) or (existing_start < end < existing_end):
                return True
        return False

class RemoteSessionOwnerTemplate(SessionOwnerTemplate):
    def __init__(self, name, ip_range = None, ua_range = None):
        SessionOwnerTemplate.__init__(self, name)
        self.set_attribute('IP', self.get_ip)
        self.set_attribute('UserAgent', self.get_ua)
        self.__ip_range__ = ip_range
        self.__ua_range__ = ua_range

    def get_ip(self):
        if self.__ip_range__:
            return np.random.choice(self.__ip_range__)
        else:
            return faker.ipv4(network=False)

    def get_ua(self):
        if self.__ua_range__:
            return np.random.choice(self.__ua_range__)
        else:
            return user_agent.generate_user_agent()
