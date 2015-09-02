"Pytest configuration"

import re

import PyTango


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
    parser.addoption("--attribute", action="append", default=["State"],
                     help="Name of a device attribute")
    parser.addoption("--desired-state", action="store",
                     help="Name of state to expect")
    parser.addoption("--undesired-state", action="store",
                     help="Name of state to not expect")


def pytest_generate_tests(metafunc):

    "Parametrize tests according to their fixtures"

    # parametrize all tests with the fixture "device"
    if "device" in metafunc.fixturenames:

        db = PyTango.Database()
        option = metafunc.config.option
        devices = set()

        # add all devices for each given server
        for srv in option.server:
            servers = db.get_server_list(srv)
            for server in servers:
                devices.update(db.get_device_class_list(server)[::2])

        # add all devices for each given class
        for cls in option.devclass:
            devices.update(db.get_device_exported_for_class(cls))

        # devices can be given as names, or wildcard patterns
        for dev in option.device:
            devices.update(db.get_device_exported(dev))

        # remove devices not matching all given devfilters
        for devfilter in option.devfilter:
            regex = re.compile(devfilter)
            devices = set(dev for dev in devices if regex.match(dev))
        metafunc.parametrize("device", list(devices))

    # likewise with "attribute" fixture, so that each of the tests
    # with that fixture will be run once for each attribute given
    if "attribute" in metafunc.fixturenames:
        metafunc.parametrize("attribute", metafunc.config.option.attribute)

    # desired/undesired states work the same way
    if "desired_state" in metafunc.fixturenames:
        if metafunc.config.option.desired_state:
            state = getattr(PyTango.DevState,
                            metafunc.config.option.desired_state.upper())
            metafunc.parametrize("desired_state", [state])
        else:
            metafunc.parametrize("desired_state", [])

    if "undesired_state" in metafunc.fixturenames:
        if metafunc.config.option.undesired_state:
            state = getattr(PyTango.DevState,
                            metafunc.config.option.undesired_state.upper())
            metafunc.parametrize("undesired_state", [state])
        else:
            metafunc.parametrize("undesired_state", [])
