## Tango smoketests ##

https://gitlab.maxlab.lu.se/kits-maxiv/lib-maxiv-tangosmoketest

This is a tiny pytest-based test suite for doing basic connectivity/functionality tests on a running Tango installation. The idea right now is to take a subset of devices and check that they can be reached, that at least some attribute can be read, and optionally checking that they are, or aren't in a given state.


### Example ###

```
py.test --devclass=AllenBradleyEIP --devfilter=R3.* --desired-state=ON --durations=10 -v -s
```

This line (executed in the project's directory) will find all devices of class "AllenBradleyEIP" and take the ones starting with "R3" (i.e. 3GeV ring devices). Then it will, for each of these:
* "Ping" it (Tango connectivity test),
* read the State attribute,
* check that the State is ON.

If any of these actions should fail, the whole test is considered failed, but it will still continue through all devices. At the end, the result for each test is printed and for all failures, whatever errors were produced. It will also print out the durations for the ten slowest tests.


### Purpose ###

Ideally, we should of course always be aware of the state of the control system through alarms etc. But we're pretty far from there at the moment. I think running something like this as a bunch of e.g. nightly jobs in Jenkins could be pretty useful, since then we'd have a dashboard summarizing the "current" state of everything, as well as the ability to go in andsee exactly what went wrong. We'd also have historical data. For really important stuff, we could even add email alerts etc.

It could also be very useful after e.g. a shutdown (planned or unplanned) when we need to get an overview of what's working and what's not.
