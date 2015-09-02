"""
Simple, general 'smoke tests' for Tango devices.

The idea is to just check basic functionality such as ping, read an
attribute, et cetera; things that should work for any device. We
don't check the results, only that the actions succeed.
"""

import PyTango


def test_ping(device):
    "Simple device connectivity test"
    proxy = PyTango.DeviceProxy(device)
    proxy.ping()


def test_read_attribute(device, attribute):
    "Check that the given attribute can be read from the device"
    proxy = PyTango.DeviceProxy(device)
    result = proxy.read_attribute(attribute)
    assert str(result.quality) == str(PyTango.AttrQuality.ATTR_VALID), (
        "Attribute quality is %s (value is %r)!" % (result.quality,
                                                    result.value))


def test_check_desired_state(device, desired_state):
    "Check that the device is in the given State"
    proxy = PyTango.DeviceProxy(device)
    state = proxy.read_attribute("State").value
    assert state == desired_state, ("State is %s, should be %s!" %
                                    (state, desired_state))


def test_check_undesired_state(device, undesired_state):
    "Check that the device is not in the given State"
    proxy = PyTango.DeviceProxy(device)
    state = proxy.read_attribute("State").value
    assert state != undesired_state, "State is %s!" % undesired_state
