## Tango smoketests ##

https://gitlab.maxlab.lu.se/kits-maxiv/lib-maxiv-tangosmoketest

This is a small pytest test suite for doing basic functionality tests on a running Tango installation. The idea right now is to take a subset of devices and check that they can be reached, that some attribute can be read, and checking that they are in a reasonable state.

If any of these actions should fail, the whole test is considered failed, but it will still continue through all devices collecting the results. At the end, a report is generated.

For more info on pytest, see http://pytest.org


### Purpose ###

Ideally, we should of course always be aware of the state of the control system through alarms etc. But we're pretty far from there at the moment. I think running something like this as a bunch of e.g. nightly jobs in Jenkins could be pretty useful, since then we'd have a dashboard summarizing the "current" state of everything, as well as the ability to go in and see exactly what went wrong. We'd also have historical data for reference. For really important stuff, we could even add email alerts etc through Jenkins.

It could also be very useful after e.g. a shutdown (planned or unplanned) when we need to get an overview of what's working and what's not. Sort of like an automated check-list.

The main point of using a testing framework like pytest for this stuff is that we'll automatically be getting neat reports in a standardized format (JUnit) that Jenkins can use for presentation.


### Usage ###

As this tool solely consists of tests, it's run with the pytest test runner, pointed to the project directory.

```
py.test <flags> <path-to-tangosmoketest>
```

If you're only interested in a particular test file, add the filename to the path (there is currently only one file anyway, the general `test_smoketest.py`). It's also possible to filter which tests are collected by adding `-k filter` to the command, e.g. `-k device`. By default, all tests are collected.

Any tests not filtered out by `-k`, but where the needed options are not given, will be skipped, so don't be surprised by that. Any test that was skipped simply was not needed to do the requested checks.

The available options specific to the project are:

`--device` Add a device to be tested. May be specified multiple times to add more devices. May use `*` as a wildcard character (but see "important note" below).

`--devclass` Add all devices matching the given class name to be tested. Can be specified multiple times, wildcards are allowed.

`--server` Add all devices in the given server. Can be specified multiple times, wildcards allowed.

`--devfilter` Give a regex that will be used to limit the devices tested to those matching the regex. This requires that some of the above options are used in order to have a list of devices to filter. Can be specified multiple times; in this case only devices matching *all* given regexes will be tested.

`--exclude` Give the name of a device to be excluded from tests, even if it matches everything above. Can be given multiple times. No regexes for this one as it would be easy to exclude devices by mistake.

`--attribute` Add an attribute to be read on all devices. May contain just the name of the attribute, or a python expression involving it. The test will fail if the attribute/expression is `False` or `None`. Note that no particular conversion is done on the value of the attribute so keep that in mind when writing your expressions. Also, it's usually safest to surround any expression with quotes (`"`) as the shell may misenterpret various characters otherwise. May be specified multiple times.

`--command` Add a command to be executed on all devices. Otherwise works like `--attribute`. Only makes sense for commands that *return* something; a command like `Init` will return `None` and therefore the test will fail.

`--desired-state` The name of a state (e.g. "ON") that the device should be in. If specified multiple times, it means that the device should be in one of the given states.

`--undesired-state` The name of a state that the device should *not* be in. By default, "FAULT" is considered undesired. If specified multiple times, it means that the device must not be in any of the given states.

Important note: when using wildcards, --device will find only *exported* devices, i.e. devices that are running. This is of course a bit dangerous since the tests will miss any devices that *should* be running but are not. The solution for now is to use `--class/--server` with  `--devfilter` or `--exclude`, or explicitly specifying each device using `--device`.


#### Useful pytest flags ###

`-s` prevents pytest from silencing prints. This will enable some sparse "debug" output which can be useful if your tests are not finding the devices you expect.

`-v` makes pytest write out a line for each test whether succeeded, skipped or failed. Useful if you really want to see exactly which tests were run with what fixtures.

`-tb=short` makes failure tracebacks more compact, by default they print the whole failing test.


For much more documentation, see pytest's homepage.


### Examples ###

```
py.test --server=AllenBradleyEIP/* 
```

This line will find all instances of servers named AllenBradleyEIP and verify that it can be "pinged" (i.e. that it't running and responds at all). It will also check that the State is not FAULT (this state is always considered "undesired").

```
py.test -k read_attribute --device=sys/tg_test/1 --device=sys/tg_test/2 --attribute=boolean_scalar
```

Will try to read the given attribute from sys/tg_test/1 and 2, checking that it's valid. 

```
py.test -v --devclass=VacuumValve --devfilter=R3-.* --desired-state=CLOSED --durations=10
```

This line will find all devices of class "VacuumValve", only taking the ones starting with "R3-". Then it will, for each of these do the basic device "health" test, and verify that the State is CLOSED.

It will also print out all test results, and the durations for the ten slowest tests.

```
py.test --device=test/eip/1 --command="len(GetBadDevices)==0" -k command
```

This will run only the command test on the "test/eip/1" device, running the "GetBadDevices" command and checking that it returns an empty list.


### Jenkins ###

In order to use Jenkins built-in features for displaying test results, add e.g. `--junit-xml=result.xml` as argument to py.test, and a JUnit post-build action to publish the test report `results.xml`. This should add a nice graph and a test result summary to the project.

Installing the "AnsiColor" plugin to Jenkins makes the test output a bit more pleasant. The AnsiColor plugin also needs to be enabled for each job. However it seems like pytest by default turns off coloring when not running interactively, so add the flag `--color=yes`.
