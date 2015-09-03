"Pytest configuration"

import re
import time

import PyTango
import pytest


def pytest_addoption(parser):

    "Add some custom flags to the py.test runner"

    parser.addoption("--devclass", action="append", default=[],
                     help="Name of a device class to check")
    parser.addoption("--device", action="append", default=[],
                     help="Name of a device (or wildcard) to check.")
    parser.addoption("--server", action="append", default=[],
                     help="Name of a server to check")
    parser.addoption("--devfilter", action="append", default=[],
                     help="Regular expression used to filter devices.")
    parser.addoption("--attribute", action="append", default=[],
                     help="Name of a device attribute")
    parser.addoption("--desired-state", action="append", default=[],
                     help="Name of State to expect")
    parser.addoption("--undesired-state", action="append", default=["FAULT"],
                     help="Name of State to not expect")


def pytest_generate_tests(metafunc):

    "Parametrize tests according to their fixtures"

    option = metafunc.config.option

    # parametrize all tests with the fixture "device"
    if "device" in metafunc.fixturenames:

        db = PyTango.Database()
        devices = set()

        # add all devices for each given server
        for srv in option.server:
            servers = db.get_server_list(srv)
            for server in servers:
                devices.update(db.get_device_class_list(server)[::2])

        # Add all devices for each given class
        for cls in option.devclass:
            devices.update(db.get_device_exported_for_class(cls))

        # devices can be given as names, or wildcard patterns
        for dev in option.device:
            devices.update(db.get_device_exported(dev))

        # remove devices not matching *all* given devfilters
        for devfilter in option.devfilter:
            regex = re.compile(devfilter)
            devices = set(dev for dev in devices if regex.match(dev))

        if not devices:
            pytest.xfail("No devices found!")

        # Let's make proxies for all the devices, that we can keep across
        # the entire test run.
        # We'll never be interested in the dserver devices, right?
        proxies = []
        for device in sorted(d for d in devices if not d.startswith("dserver/")):
            proxies.append(PyTango.DeviceProxy(device))
            time.sleep(0.1)

        # Note: the ids argument provides a way for pytest to get the device name
        # from the proxy, for more readable presentation.
        metafunc.parametrize("device", proxies, scope="session", ids=lambda p: p.name())

    # likewise with "attribute" fixture, so that each of the tests
    # with that fixture will be run once for each attribute given
    if "attribute" in metafunc.fixturenames:
        metafunc.parametrize("attribute", option.attribute)

    # and for the states...
    if "desired_states" in metafunc.fixturenames:
        states = [getattr(PyTango.DevState, s.upper()) for s in option.desired_state]
        if states:
            metafunc.parametrize("desired_states", [states], ids=lambda s: ",".join(map(str, s)))
        else:
            metafunc.parametrize("desired_states", [])

    if "undesired_states" in metafunc.fixturenames:
        states = [getattr(PyTango.DevState, s.upper()) for s in option.undesired_state]
        if states:
            metafunc.parametrize("undesired_states", [states], ids=lambda s: ",".join(map(str, s)))
        else:
            metafunc.parametrize("undesired_states", [])
