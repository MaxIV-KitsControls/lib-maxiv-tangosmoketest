"""
Simple, general 'smoke tests' for Tango devices.

The idea is to just check basic functionality such as ping, read an
attribute, et cetera; things that should work for any device. We
don't check the results, only that the actions succeed.
"""

import re

import PyTango
import pytest


# === Helpers ===

def find_variable(expression):
    """Find the variable in an 'ask for forgiveness, not permission' way"""
    try:
        eval(expression)
    except NameError as ne:
        return re.findall("name '(\w+)' is not defined", str(ne))[0]


# === Tests ===

def test_ping(device):
    """Check that we can even connect to the device."""
    device.ping()


def test_state(device, desired_states, undesired_states):

    """
    Check the device's State.
    If a list of desired states is given, we check that the state
    is one of those, otherwise verify that it's *not* in the list of
    undesired states.
    """

    state = device.read_attribute("State").value
    if desired_states:
        assert state in desired_states, "State is %s!" % state
    if undesired_states:
        assert state not in undesired_states, "State is %s!" % state


def test_attribute(device, attribute, recwarn):

    """
    Read a given attribute and optionally do some logic check on the
    value, e.g. "A==0", "0<abs(B)<=67", "len(Errors)==0". It's
    possible to do arbitrary builtin python operations in the
    attribute expression (within reason...).

    Consider the type of the attribute, no automatic conversion will
    be done!

    Also, (currently) only one attribute can be used in the expression.
    """

    name = find_variable(attribute)
    if not name:
        pytest.xfail("No attribute specified in '%s'?" % name)

    result = device.read_attribute(name)

    assert result.quality == PyTango.AttrQuality.ATTR_VALID, (
        "Attribute quality is %s (value is %r)!" % (result.quality, result.value))

    assert eval(attribute, {name: result.value}) not in (False, None), (
        "Attribute check failed! (%s is %r)" % (name, result.value))


def test_command(device, command):

    """Run a given command. Otherwise works like test_attribute w.r.t
    expressions, e.g. "GetBadTags=[]"
    """

    # find the name of the command in an "ask for forgiveness, not permission" way
    name = find_variable(command)
    if not name:
        pytest.xfail("No command specified?")

    result = device.command_inout(name)

    assert eval(command, {name: result}) not in (False, None), (
        "Command check '%s' failed! (%s() returned %r)" % (command, name, result))
