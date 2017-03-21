from __future__ import division
from builtins import range
from past.utils import old_div
from builtins import object
import datetime as dt
from random import randrange, random, choice, randint
import uuid
from collections import OrderedDict
import numpy as np
import calendar
import abc
from evgen.events import EventGroup, GenericEventTemplate
from copy import copy
import user_agent
from faker import Faker

def random_test(probability):
    if random() < probability:
        return True
    else:
        return False

class SessionTemplate(object):
    def __init__(self, event_delay=1000, start_date=None, session_id=None, generate_session_id=True,  session_delay=1000, session_random=0):
        self.__user__ = UserProfile()
        self.__events__ = []
        self.__event_delay__ = event_delay
        self.__session_delay__ = dt.timedelta(milliseconds=session_delay)
        self.__sdr__ = session_random
        self.__generate_sid__ = generate_session_id
        self.__writers__ = []
        if session_id:
            self._sid_ = session_id
        else:
            self._sid_ = uuid.uuid4().hex
        if start_date is None: start_date = dt.datetime.strptime("2016-01-01 01:00:00", "%Y-%m-%d %H:%M:%S")
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
        eg.add_event(event, probability, delay,delay_random)
        self.__events__.append(eg)
    
    def add_event_group(self, event_group):
        self.__events__.append(event_group)

    def add_user(self, user_profile):
        self.__user__ = user_profile

    def __generate_session_id__(self):
        self._sid_ = uuid.uuid4().hex

    def display(self):
        """
        Sends recently generated event session to all registered sinks.
        """
        for e in self.__formatted_events__:
            e.generate()

    def get(self):
        """
        Returns recently generated event session as list of formatted events
        """
        return self.__formatted_events__
     
    def add_writer(self, writer):
        for eg in self.__events__:
            for e in eg.events:
                e[0].add_writer(writer)


    def generate(self, start_date=None, display=True):
        if self.__generate_sid__:
            self.__generate_session_id__()
        if start_date:
            self.set_start_date(start_date)
        delay = 0
        session_events = []
        self.__formatted_events__ = []
        #retrieving all static and dynamic user properties - they may change between sessions (i.e. IP)
        user_properties = self.__user__.Properties
        for eg in self.__events__:
            for i in range(randrange(eg.min_repeat, eg.max_repeat+1)):
                for e in eg.events:
                    if random_test(e[1]):
                        e[0].TimeStamp = self.start_date+dt.timedelta(milliseconds=delay)
                        e[0].SessionId = self._sid_
                        #updating dictionary with UserProfile properties
                        e[0].__dict__.update(user_properties)
                        self.__formatted_events__.append(copy(e[0]))
                        if e[3]: #including random delay
                            i = randrange(-(e[2]*e[3]), (e[2]*e[3]))
                            delay += e[2]+i
                        else: 
                            delay += e[2]
                        self.last_session_end = e[0].TimeStamp
        if display:
            self.display()

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

class UserTemplate(object):
    def __init__(self, user_profile, number_of_sessions, randomize_sessions=True, start_date=None, end_date=None):
        #uniform distributions by default
        self.h_dist = HourlyDistribution()
        self.m_dist = MonthlyDistribution()
        self.d_dist = WeeklyDistribution()
        self.sessions = []
        self.randomize_sessions = randomize_sessions
        self.s_dist = None #session distribution
        self.__user__ = user_profile
        self.__nos__ = number_of_sessions
        if start_date is None: start_date = dt.datetime.now()
        self.start_date = start_date
        if end_date is None: end_date = self.start_date + dt.timedelta(days=30)
        self.end_date = end_date
        self.session_dates = []

    
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
        if self.__user__:
            session.add_user(self.__user__)
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

    def generate(self, sorted=False, display=True):
        formatted_sessions = [] #used to sort sessions after generation
        session_count = 0
        if self.s_dist is None:
            self.s_dist = Distribution(sample_size=len(self.sessions))
        begin = self.start_date
        while session_count < self.__nos__:
            if self.randomize_sessions:
                begin = self.__generate_random_date__()
            session = self.sessions[self.s_dist.get_value()]
            session.generate(start_date=begin, display=False)
            end = session.last_session_end 
            if self.randomize_sessions:                     
                if not self.__test_date_intersect__(begin, end) and end < self.end_date:
                    if sorted:
                        formatted_sessions.append((begin,session.get()))
                    else: 
                        session.display()
                    self.session_dates.append((begin,end))
                    session_count += 1
            else:
                begin = end
                session.display()
                session_count += 1
        if sorted:        
            formatted_sessions.sort()
            for s in formatted_sessions:
                for l in s[1]:
                    l.generate()

    def __test_date_intersect__(self, begin, end):
        """
        Verify whether new session (described as beginning and end datetime object) overlaps with already existing ones.
        """
        for existing_start, existing_end in self.session_dates:
            if (existing_start < begin <existing_end) or (existing_start < end < existing_end):
                return True
        return False


class Distribution(object):
    def __init__(self, elements=None, sample_size=None, weights=None):
        if elements is None and sample_size is None:
            raise ValueError('either elements or sample_size parameter is required')
        if elements is None:
            self.__elements__ = list(range(0,sample_size))
        else:
            self.__elements__ = elements
        if weights is None:

            self.__weights__ = [old_div(1.0,len(self.__elements__))]*len(self.__elements__)
        else:
            self.__weights__ = weights
        
    def get_value(self, starts=None, ends=None):
        """
        Generates random value based on provided elements and weights (probability distribution).
        Supports also subset of all elements.
        starts - beginning of subset
        ends = end of subset
        """
        if starts is None: starts== 0
        if ends is None: ends == len(self.__elements__)
        sprob = sum(self.__weights__[starts:ends])
        elements = self.__elements__[starts:ends]
        weights = [old_div(w,sprob) for w in self.__weights__[starts:ends]]
        return np.random.choice(elements, size=1, p=weights)[0]


class WeeklyDistribution(Distribution):
    def __init__(self, weights=None):
        super(WeeklyDistribution, self).__init__(elements=list(range(0,7)), weights=weights)

    def get_value(self, year, month):
        day_of_week = np.random.choice(self.__elements__, size=1, p=self.__weights__)[0]
        #turning day_of_week into absolute day number
        mcal = calendar.Calendar(0).monthdayscalendar(year, month)
        day = np.random.choice([i[day_of_week] for i in mcal if i[day_of_week] != 0], size=1)[0]
        return day

class HourlyDistribution(Distribution):
    def __init__(self, weights=None):
        super(HourlyDistribution, self).__init__(elements=list(range(0,24)), weights=weights)

class MonthlyDistribution(Distribution):
    def __init__(self, weights=None):
        super(MonthlyDistribution, self).__init__(elements=list(range(1,13)), weights=weights)
            

class UserProfile(object):
    def __init__(self, name=None):
        super(UserProfile, self).__setattr__('__static_properties__', {})
        super(UserProfile, self).__setattr__('__dynamic_properties__', {})
        self.set_property('UserName', name)

    def __getattr__(self, val):
        if val=="Properties":
            props = self.__static_properties__
            #materializing dynamic properties and adding them to main dictionary
            props.update({k : self.__dynamic_properties__[k]() for k in self.__dynamic_properties__})
            return props
        elif val in self.__static_properties__: 
            return self.__static_properties__.get(val)
        elif val in self.__dynamic_properties__:
            return self.__dynamic_properties__.get(val)()
        else:
            raise AttributeError("Property: %s does not exist" % val)
            #return super(UserProfile, self).__properties__.get(val)

    def set_property(self, key, value):
        self.__static_properties__[key] = value

    def get_property(self, key):
        self. __static_properties__.get(key)

    def set_dynamic_property(self, key, method):
        self.__dynamic_properties__[key] = method

class RemoteUserProfile(UserProfile):
    def __init__(self, name, ip_range = None, ua_range = None):
        super(RemoteUserProfile, self).__init__(name)
        self.set_dynamic_property('IP', self.get_ip)
        self.set_dynamic_property('UserAgent', self.get_ua)
        self.__ip_range__ = ip_range
        self.__ua_range__ = ua_range

    def get_ip(self):
        if self.__ip_range__:
            return np.random.choice(self.__ip_range__)
        else:
            return Faker().ipv4(network=False)

    def get_ua(self):
        if self.__ua_range__:
            return np.random.choice(self.__ua_range__)
        else:
            return user_agent.generate_user_agent()
