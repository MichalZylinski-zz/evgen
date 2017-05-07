## Code samples

In [/examples](https://github.com/MichalZylinski/evgen/tree/master/examples) directory you may find plenty of useful code snippets that present the way evgen framework can be used:
* [basic.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/basic.py) - shows most basic usage of evgen. It generates single *SessionTemplate* object that consists of 2 generic events named "START" and "STOP". Once executed, both of them will be displayed in console.

* [timeseries.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/timeseries.py) - introduces *EventGroup* class and creates custom event class called *TemperatureEventTemplate*. It will generate and present random temperature value and display it in console.

* [timeseries_server.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/timeseries_server.py) - takes the previous example and runs it in real-time mode, trying to simulate real user's behaviour.

* [rabbitmq.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/rabbitmq.py) - sends temperature events to RabbitMQ queue.

* [timeseries_stateful.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/timeseries_stateful.py) - presents a way to maintain status between multiple events. It can be achieved by using *SessionTemplate*'s attributes dictionary. As the result temperature events will not be random anymore, but will gradually increase over time.

* [custom_sink.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/custom_sink.py) - demonstrates the possibility of connecting the same session data to multiple outputs and formats. The code takes two basic events ("START" and "STOP") and sends them to two separate, custom writers using JSON and CSV format.

* [directory_writer.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/directory_writer.py) - introduces *SessionOwnerTemplate* class and presents the way to write session data as series of individual files (instead on single big one).

* [finance_demo.py](https://raw.githubusercontent.com/MichalZylinski/evgen/master/examples/finance_demo.py) - end-to-end demo, showcasing most of evgen framework capabilities. It tries to simulate bank user behaviour: creates custom user (*BankUserProfile*) and event (*MoneyTransferEventTemplate*) classes and then defines relationships between session events using probability distributions. The end result are 10 separate user sessions sent to console.