"""
Simple, general 'smoke tests' for Tango devices.

The idea is to just check basic functionality such as ping, read an
attribute, et cetera; things that should work for any device. We
don't check the results, only that the actions succeed.
"""

import operator

import PyTango


def test_ping(device):
    "Simple device connectivity test"
    device.ping()


def test_read_attribute(device, attribute):
    "Check that the given attribute can be read from the device"

    # TODO: this can be done more elegantly...
    if "==" in attribute:
        attr, value = attribute.split("==")
        value = float(value)
        check = operator.eq
    elif "!=" in attribute:
        attr, value = attribute.split("!=")
        value = float(value)
        check = operator.ne
    elif ">=" in attribute:
        attr, value = attribute.split(">=")
        value = float(value)
        check = operator.ge
    elif ">" in attribute:
        attr, value = attribute.split(">")
        value = float(value)
        check = operator.gt
    elif "<=" in attribute:
        attr, value = attribute.split("<=")
        value = float(value)
        check = operator.le
    elif "<" in attribute:
        attr, value = attribute.split("<")
        value = float(value)
        check = operator.lt
    else:
        attr = attribute
        check = lambda *_: True

    result = device.read_attribute(attr)
    assert result.quality == PyTango.AttrQuality.ATTR_VALID, (
        "Attribute quality is %s (value is %r)!" % (result.quality, result.value))
    assert check(result.value, value), attribute + (" (%s is %r)" % (attr, result.value))


def test_check_desired_state(device, desired_states):
    "Check that the device is in the given State"
    state = device.read_attribute("State").value
    assert state in desired_states, "State is not %s!" % state


def test_check_undesired_state(device, undesired_states):
    "Check that the device is not in the given State"
    state = device.read_attribute("State").value
    assert state not in undesired_states, "State is %s!" % state
