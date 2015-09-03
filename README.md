## Tango smoketests ##

https://gitlab.maxlab.lu.se/kits-maxiv/lib-maxiv-tangosmoketest

This is a small pytest-based test suite for doing basic connectivity/functionality tests on a running Tango installation. The idea right now is to take a subset of devices and check that they can be reached, that some attribute can be read, and checking that they are in a reasonable state.

If any of these actions should fail, the whole test is considered failed, but it will still continue through all devices collecting the results. At the end, a report is generated.

*Important note*: the --devclass (and --device when using wildcards) argument will find only *exported* devices, i.e. devices that are running. This is of course a bit dangerous since the tests will miss any devices that *should* be running but are not. I haven't yet found a good workaround for this. The solution for now is to use --server or explicitly specifying each device using --device. 


### Purpose ###

Ideally, we should of course always be aware of the state of the control system through alarms etc. But we're pretty far from there at the moment. I think running something like this as a bunch of e.g. nightly jobs in Jenkins could be pretty useful, since then we'd have a dashboard summarizing the "current" state of everything, as well as the ability to go in and see exactly what went wrong. We'd also have historical data. For really important stuff, we could even add email alerts etc through Jenkins.

It could also be very useful after e.g. a shutdown (planned or unplanned) when we need to get an overview of what's working and what's not. Sort of like an automated check-list.


### Examples ###

```
py.test --server=AllenBradleyEIP/* 
```

This line will find all instances of servers named AllenBradleyEIP and verify that it can be "pinged" (i.e. that it't running and responds at all). It will also check that the State is not FAULT (the undesired_state test is aways run).

```
py.test -k read_attribute --device=sys/tg_test/1 --device=sys/tg_test/2 --attribute=boolean_scalar
```

Will try to read the given attribute from sys/tg_test/1 and 2, checking that it's valid. 

```
py.test -v --devclass=VacuumValve --devfilter=R3-.* --desired-state=CLOSED --durations=10
```

This line will find all devices of class "VacuumValve" and take the ones starting with "R3-" (i.e. 3GeV ring devices). Then it will, for each of these:

* "Ping" it (Tango connectivity test),
* check that the State is CLOSED.

It will also print out all test results, and the durations for the ten slowest tests.


### Jenkins ###

In order to use Jenkins built-in features for displaying test results, add "--junitxml=result.xms" as argument to py.test, and a JUnit post-build action to publish the test report "results.xml". This will add a nice graph and a test result summary to the project.

Installing the "AnsiColor" plugin to Jenkins makes the test output a bit more pleasant. The AnsiColor plugin also needs to be enabled for each job. However it seems like pytest by default turns off coloring when not running interactively, so add the flag "--color=yes".
