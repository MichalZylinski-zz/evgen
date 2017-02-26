from evgen.core import SessionTemplate,  HourlyDistribution, WeeklyDistribution, MonthlyDistribution, UserTemplate, RemoteUserProfile
from evgen.writers import ConsoleWriter
from evgen.events import GenericEventTemplate, EventGroup, CSVEventFormat
from random import randint, choice

from random import randrange
from datetime import timedelta

from schwifty import IBAN

def generateIBAN():
    bank_range = ['10200110', '10201543', '10205532']
    return IBAN.generate("PL", bank_code=choice(bank_range), account_code=str(randint(1,pow(10,16)))).formatted

class BankUserProfile(RemoteUserProfile):
    """
    BankUserProfile extens RemoteUserProfile class with 2 dynamic properties:
     - FromIBAN - source IBAN account number
     - ToIBAN - destination IBAN account number
     Both of them may rely on fixed number of accounts provided by from_IBAN_range and to_IBAN_range parameters.
    """
    def __init__(self, name, ip_range=None, ua_range=None, from_IBAN_range=None, to_IBAN_range=None):
        super(BankUserProfile, self).__init__(name, ip_range, ua_range)
        self.__from_IBAN__ = from_IBAN_range
        self.__to_IBAN__ = to_IBAN_range
        self.set_dynamic_property('FromIBAN', self.get_from_IBAN)
        self.set_dynamic_property('ToIBAN', self.get_to_IBAN)

    def get_from_IBAN(self):
        if self.__from_IBAN__:
            return choice(self.__from_IBAN__)
        else:
            return generateIBAN()

    def get_to_IBAN(self):
        if self.__to_IBAN__:
            return choice(self.__to_IBAN__)
        else:
            return generateIBAN()

class MoneyTransferEventTemplate(GenericEventTemplate):
    """
    MoneyTransferEventTemplate extends generic template with new dynamic 'Transfer' property containing value of bank transaction.

    All it takes to extend GenericEventTemplate with dynamically generated values is to override preprocess method with new public property definition. 
    """

    def __init__(self, *args, **kwargs):
        super(MoneyTransferEventTemplate, self).__init__("Transfer", *args, **kwargs)
        self.set_transaction_range()

    def set_transaction_range(self, min_value=1, max_value=100):
        """
        Sets boundaries for Transfer property value.
        """
        self.__min__ = min_value
        self.__max__ = max_value

    def preprocess(self):
        self.Value = round(randrange(self.__min__, self.__max__), 2)

#Defining event writers and formats
generic_conn = ConsoleWriter(format=CSVEventFormat(fields=["TimeStamp", "IP", "UserName", "SessionId", "Name"], quote="\""))
money_transfer_conn = ConsoleWriter(format=CSVEventFormat(fields=["TimeStamp", "UserName", "SessionId", "Name","FromIBAN", "ToIBAN", "Value"]))

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
genericSession = SessionTemplate(session_random=0.02, generate_session_id=True)
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

u_profile = BankUserProfile('jdoe')

import datetime

start = datetime.datetime.strptime("2014-01-01 01:00:00", "%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime("2016-12-31 23:59:00", "%Y-%m-%d %H:%M:%S")

user1 = UserTemplate(u_profile, number_of_sessions=10, start_date=start, end_date=end)

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
user1.generate(sorted=True)
    