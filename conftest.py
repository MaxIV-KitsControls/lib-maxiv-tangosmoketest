"Pytest configuration"

import re

import PyTango


def pytest_addoption(parser):

    "Add some custom flags to the py.test runner"

    parser.addoption("--devclass", action="append", default=[],
                     help="Name of a device class to check")
    parser.addoption("--device", action="append", default=[],
                     help="Name of a device (or wildcard) to check.")
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
        devices = set()
        devices.update(metafunc.config.option.device)
        db = PyTango.Database()
        option = metafunc.config.option
        for cls in option.devclass:
            devices.update(db.get_device_exported_for_class(cls))
        for dev in option.device:
            devices.update(db.get_device_exported(dev))
        for devfilter in option.devfilter:
            regex = re.compile(devfilter)
            devices = set(dev for dev in devices if regex.match(dev))
        print devices
        metafunc.parametrize("device", list(devices))

    # likewise with "attribute" fixture
    if "attribute" in metafunc.fixturenames:
        metafunc.parametrize("attribute", metafunc.config.option.attribute)

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
