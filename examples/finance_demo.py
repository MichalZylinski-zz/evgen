#!/usr/bin/env python

from builtins import str
from evgen.core import SessionTemplate,  HourlyDistribution, WeeklyDistribution, MonthlyDistribution,  RemoteSessionOwnerTemplate, GenericEventTemplate, EventGroup
from evgen.writers import ConsoleWriter
from evgen.formats import CSVEventFormat
from random import randint, choice
import numpy as np
from datetime import timedelta

import datetime

np.random.seed(12345678)

def generateIBAN():
    return ''.join([str(np.random.randint(1,9)) for i in range(1,30)])


class BankUserProfile(RemoteSessionOwnerTemplate):
    """
    BankUserProfile extens RemoteUserProfile class with 2 dynamic properties:
     - FromIBAN - source IBAN account number
     - ToIBAN - destination IBAN account number
     Both of them may rely on fixed number of accounts provided by from_IBAN_range and to_IBAN_range parameters.
    """
    def __init__(self, name, ip_range=None, ua_range=None, from_IBAN_range=None, to_IBAN_range=None):
        RemoteSessionOwnerTemplate.__init__(self, name, ip_range, ua_range)
        self.__from_IBAN__ = from_IBAN_range
        self.__to_IBAN__ = to_IBAN_range


class MoneyTransferEventTemplate(GenericEventTemplate):
    """
    MoneyTransferEventTemplate extends generic template with new dynamic 'Transfer' property containing value of bank transaction.

    All it takes to extend GenericEventTemplate with dynamically generated values is to override preprocess method with new public property definition. 
    """

    def __init__(self, *args, **kwargs):
        GenericEventTemplate.__init__(self, "Transfer", *args, **kwargs)
        self.set_transaction_range()
        self.set_attribute("Value", self.get_value)
        self.set_attribute('FromIBAN', self.get_from_IBAN)
        self.set_attribute('ToIBAN', self.get_to_IBAN)


    def set_transaction_range(self, min_value=1, max_value=100):
        """
        Sets boundaries for Transfer property value.
        """
        self.__min__ = min_value
        self.__max__ = max_value

    def get_value(self):
        return np.random.randint(self.__min__, self.__max__)


    def get_from_IBAN(self):
        return choice(self.Owner.__from_IBAN__)

    def get_to_IBAN(self):
        return choice(self.Owner.__to_IBAN__)

#Defining event writers and formats
generic_conn = ConsoleWriter(format=CSVEventFormat(fields=["TimeStamp", "IP", "UserName", "SessionId", "Name"]))
money_transfer_conn = ConsoleWriter(format=CSVEventFormat(fields=["TimeStamp", "IP", "UserName", "SessionId", "Name","FromIBAN", "ToIBAN", "Value"]))

#Defining basic events
signin_event = GenericEventTemplate(name="Signin")
signin_event.add_writer(generic_conn)

signout_event = GenericEventTemplate(name="Signout")
signout_event.add_writer(generic_conn)

list_event = GenericEventTemplate(name="ListOperations")
list_event.add_writer(generic_conn)

transfer_event = MoneyTransferEventTemplate()
transfer_event.set_transaction_range(50,2000)
transfer_event.add_writer(money_transfer_conn)

#Defining session template
genericSession = SessionTemplate(session_random=0.02)
genericSession.set_start_date('2016-03-12 15:00:00')
genericSession.add_event(signin_event, probability=1, delay=5000, delay_random=0.2)

#creating event group
e_group = EventGroup()
e_group.add_event(list_event, probability=0.6, delay=2000, delay_random=None)
e_group.add_event(transfer_event, probability=0.8)
e_group.add_event(transfer_event, probability=0.4)
e_group.set_repeat_policy(2,10)
genericSession.add_event_group(e_group)
genericSession.add_event(signout_event, probability=0.8)
genericSession.add_session_delay(time_delta = timedelta(days=1))

#Defining user template
hDist = HourlyDistribution([0,0,0,0,0,0,0,0.1,0.3,0.2,0,0.1,0.1,0.1,0.1,0,0,0,0,0,0,0,0,0])
dDist = WeeklyDistribution([0.2,0.2,0.2,0.2,0.2,0,0])
mDist = MonthlyDistribution([0,0.2,0.1, 0.1,0.05,0.1,0.1,0.1,0.1,0.1,0.05,0])


start = datetime.datetime.strptime("2014-01-01 01:00:00", "%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime("2016-12-31 23:59:00", "%Y-%m-%d %H:%M:%S")

iban_range = [generateIBAN() for i in range(10)]
user1 = BankUserProfile("jdoe", from_IBAN_range=iban_range, to_IBAN_range=iban_range)
user1.set_number_of_sessions(10)
user1.set_start_date(start)
user1.set_end_date(end)

#Defining temporal distribution
user1.add_daily_distribution(dDist)
user1.add_hourly_distribution(hDist)
user1.add_session(genericSession)

"""
You may add multiple sessions to user profile. 

user1.add_session([additional session])

You may also define probability distribution for sessions:

user1.add_session_distribution([0.7,0.1,0.2])
"""
user1.generate()
    