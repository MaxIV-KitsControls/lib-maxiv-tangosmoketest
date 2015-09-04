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
    parser.addoption("--exclude", action="append", default=[],
                     help="A device to exclude from tests")
    parser.addoption("--attribute", action="append", default=[],
                     help="Name of a device attribute")
    parser.addoption("--command", action="append", default=[],
                     help="Name of a device command")
    parser.addoption("--desired-state", action="append", default=[],
                     help="Name of State to expect")
    parser.addoption("--undesired-state", action="append", default=["FAULT"],
                     help="Name of State to not expect")


def pytest_configure(config):

    """Collect relevant devices from the database and setup proxies"""

    db = PyTango.Database()
    devices = set()

    # add all devices for each given server
    for srv in config.option.server:
        servers = db.get_server_list(srv)
        for server in servers:
            devices.update(db.get_device_class_list(server)[::2])

    # Add all devices for each given class
    for cls in config.option.devclass:
        devices.update(db.get_device_name("*", cls))

    # devices can be given as names, or wildcard patterns
    for dev in config.option.device:
        devices.update(db.get_device_exported(dev))

    print "Found %d devices in the database" % len(devices)

    # remove devices not matching *all* given devfilters
    for devfilter in config.option.devfilter:
        n = len(devices)
        regex = re.compile(devfilter, flags=re.IGNORECASE)
        devices = set(dev for dev in devices if regex.match(dev))
        print "Filter '%s' matched %d devices" % (devfilter, len(devices))

    # Exclude unwanted devices
    # We'll never be interested in the dserver devices, right?
    exclude = [e.lower() for e in config.option.exclude]
    devices = [d for d in devices
               if not d.lower().startswith("dserver/")]

    n = len(devices)
    devices = [d for d in devices if not d.lower() in exclude]

    print "Excluded %d devices" % (n - len(devices))

    if not devices:
        pytest.xfail("No devices found!")

    # Let's make proxies for all the devices, that we can keep across
    # the entire test run.
    config.proxies = []
    for device in sorted(devices):
        config.proxies.append(PyTango.DeviceProxy(device))
        time.sleep(0.1)

    print "Created proxies to %d devices" % len(config.proxies)


def pytest_generate_tests(metafunc):

    "Parametrize tests according to their fixtures"

    option = metafunc.config.option

    # parametrize all tests with the "device" fixture to be run for each device
    if "device" in metafunc.fixturenames:
        # Note: the ids argument provides a way for pytest to get the device name
        # from the proxy, for more readable presentation.
        metafunc.parametrize("device", metafunc.config.proxies, scope="session",
                             ids=lambda p: p.dev_name().upper())

    # likewise with "attribute" fixture
    if "attribute" in metafunc.fixturenames:
        metafunc.parametrize("attribute", option.attribute, scope="session")

    if "command" in metafunc.fixturenames:
        metafunc.parametrize("command", option.command, scope="session")

    # we don't run each test once per State given, the tests get them as a list
    if "desired_states" in metafunc.fixturenames:
        states = [getattr(PyTango.DevState, s.upper()) for s in option.desired_state]
        if states:
            metafunc.parametrize("desired_states", [states], ids=lambda s: ",".join(str, s), scope="session")
        else:
            metafunc.parametrize("desired_states", [[]], ids="*", scope="session")

    if "undesired_states" in metafunc.fixturenames:
        states = [getattr(PyTango.DevState, s.upper()) for s in option.undesired_state]
        if states:
            metafunc.parametrize("undesired_states", [states],
                                 ids=lambda s: ",".join(map(lambda z: "!%s" % z, s)), scope="session")
        else:
            metafunc.parametrize("undesired_states", [[]], ids="*", scope="session")
