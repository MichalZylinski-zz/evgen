import abc
from evgen.events import CSVEventFormat
import os, time

class GenericWriter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, format=None):
        if format is None:
            format = CSVEventFormat()
        self.Format = format

    @abc.abstractmethod
    def send(self, event):
        """Sends event to sink"""
        return 

class FileWriter(GenericWriter):
    def __init__(self, file_name, format = None, mode="a"):
        self.__output__ = open(file_name, mode)
        super(FileWriter, self).__init__(format=format)

    def send(self, event):
        v = self.Format.format(event)
        if v[-1] != "\n":
            v += "\n"
        self.__output__.write(v)

class EventHubWriter(GenericWriter):
    """
    EventHubWriter sends all the events to Microsoft Azure Event Hub Service.
    """
    def __init__(self, eh_name, connection_string, format=None):
        from azure.servicebus import EventHub, ServiceBusService
        """
        eh_name - Event Hub service name
        connection_string - Event Hub namespace connection string
        """
        conn_dict = {i.split('=',1)[0]:i.split('=',1)[1] for i in connection_string.split(';')}
        ns_name = conn_dict['Endpoint'].replace('sb://','').replace('.servicebus.windows.net/','')      
        self.__sbs__ = ServiceBusService(service_namespace=ns_name, shared_access_key_name=conn_dict['SharedAccessKeyName'],shared_access_key_value=conn_dict['SharedAccessKey'])
        self.__ehname__ = eh_name
        super(EventHubWriter, self).__init__(format=format)

    def send(self, event):
        #converting datetime timestamp to ISO 8601 format
        event['TimeStamp'] = event['TimeStamp'].isoformat()+"Z"
        try:
            self.__sbs__.send_event(self.__ehname__, self.Format.format(event))
        except:
            #adding small delay in case the there is temporary connection issue with Event Hub
            time.sleep(1)
            try:
                self.__sbs__.send_event(self.__ehname__, self.Format.format(event))
            except:
                raise IOError("Cannot send message to Event Hub service")
        

class DirectoryWriter(GenericWriter):
    """
    DirectoryWriter creates separate file per session and stores them in predefined directory.
    """
    def __init__(self, directory_name, extension=".log", format = None, mode="a"):
        self.__directory__ = directory_name
        if directory_name not in os.listdir('.'):
            os.mkdir(self.__directory__)
        self.__mode__ = mode
        self.__sid__ = None
        self.__sink__ = None
        self.__extension__ = extension
        super(DirectoryWriter, self).__init__(format=format)

    def send(self, event):
        if self.__sid__ != event['SessionId']:
            self.__sink__ = open(self.__directory__+"/"+event['SessionId']+self.__extension__, self.__mode__)
        v = self.Format.format(event)
        if v[-1] != "\n":
            v += "\n"
        self.__sink__.write(v)


class ConsoleWriter(GenericWriter):
    def send(self, event):
        print self.Format.format(event)

