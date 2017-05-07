# evgen

Comprehensive event generation framework.

### Motivation

Have you ever had a need to create some meaningful data? Say, large set of log files that will comply to certain structure or series of events that are NOT fully random?

This is the reason why evgen(a.k.a. **ev**ent **gen**erator) was born. Its sole purpuse is to help you simulate data on your terms. It has been written and supports both Python 2 and 3.

As for now evgen supports out of the box:

* Highly flexible architecture to deal with complex business scenarios
* JSON and CSV file formats (and ability to support virtually any format you may imagine)
* RabbitMQ and Azure Event Hubs connectivity for real-time message generation

### Installation

The easiest way to start using evgen is by using **pip**.:

```
pip install evgen
```

It comes together with a few useful samples (see *examples* directory)

### Your first evgen project

Let's study the most basic example of evgen usage (you may find full source code in *examples\basic.py*). We start with loading several necessary classes:

```python
from evgen.core import SessionTemplate, GenericEventTemplate
from evgen.writers import ConsoleWriter
```
Next we're defining a session containing two types of events - "start" and "stop". While registering the event we can define also 2 other very important properties: **probability** (value between 0 and 1 saying what are the odds this particular event will happen) and **delay** (numeric value in milliseconds describing the distance to next event): 

```python
session = SessionTemplate()
session.add_event(GenericEventTemplate("start"), probability = 1, delay=5000)
session.add_event(GenericEventTemplate("stop"), probability = 1)
```
To make it easy, our session will simply print the contents to standard console. This can be achieved by attaching relevant writer and calling **generate()** method:

```python
session.add_writer(ConsoleWriter())
session.generate()
```
Here's the final output (notice 5 sec delay between the events):
```
2017-04-10 20:39:45.687000,685ce816a9d943328e68c7cf938a7f2e,start
2017-04-10 20:39:50.657000,685ce816a9d943328e68c7cf938a7f2e,stop
```


### Next steps

* High-level architecture and building blocks description
* [More cool examples](https://github.com/MichalZylinski/evgen/blob/master/docs/examples.md)


