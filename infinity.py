#!/usr/bin/env python

import argparse
import ConfigParser
import importlib
import os
import sys
import signal
import inflogging
from v12n import base
from inftest import InfinityTest
from infexceptions import InfinityException, InfinityTestException
from xpresserng import ImageNotFound


def load_config(path):
    config = ConfigParser.RawConfigParser()
    config.read(path)
    conf = {
        "connection": "qemu:///system",
        "logs": "/var/log/infinity",
        "pool": "/tmp/infinity-disks"
    }
    try:
        if config.has_option("general", "conn"):
            conf["connection"] = config.get("general", "conn")
        if config.has_option("general", "logs"):
            conf["logs"] = config.get("general", "logs")
        if config.has_option("general", "pool"):
            conf["pool"] = config.get("general", "pool")
    except ConfigParser.NoSectionError:
        pass
    return conf


def load_tests(path):
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(path, "inftests.cfg"))  # TODO: error

    tests = []
    for section in config.sections():
        name = config.get(section, "name")
        record = config.getboolean(section, "record")
        module = config.get(section, "module")

        get_option = lambda option: config.get(section, option) if os.path.isabs(
            config.get(section, option)) else os.path.join(path, config.get(section, option))

        vm_xml_path = get_option("vm")
        xml_file = open(vm_xml_path)
        vm_xml = xml_file.read()
        xml_file.close()

        storage_xml_path = get_option("storage")
        xml_file = open(storage_xml_path)
        storage_xml = xml_file.read()
        xml_file.close()

        images = get_option("images")
        live_medium = get_option("live_medium")

        try:
            imported_module = importlib.import_module(module + ".main")
            main = imported_module.main
        except ImportError:
            raise InfinityException("Test module " + module + " cannot be imported.")

        tests.append(InfinityTest(name, record, main, vm_xml, storage_xml, live_medium, images))

    return tests


def sigint_signal(signum, frame):
    if signum == signal.SIGTERM:
        base.clean_all()
        sys.exit(0)
    while True:
        clean = raw_input("Clean virtual machines? [Y/n]: ")
        if clean in ["", "Y", "y"]:
            base.clean_all()
            sys.exit(0)
        if clean in ["n", "N"]:
            sys.exit(0)


def run(path, config, verbose):
    failed = []
    passed = []
    errors = []
    sys.path.insert(0, path)
    tests = load_tests(path)
    inflogging.setup_logging(config["logs"])
    base.setup_v12n(config["connection"], config["pool"])

    for test in tests:
        test.build_vm()

        try:
            test.run()

        except InfinityTestException as e:
            test.message = e.message
            if verbose:
                sys.stderr.write(test.message + "\n")
            inflogging.log(test.message, "ERROR")
            failed.append(test)
        except ImageNotFound as e:
            test.message = "Image not found: "+str(e.message)
            if verbose:
                sys.stderr.write(test.message + "\n")
            inflogging.log(test.message + "\n", "ERROR")
            failed.append(test)
        except InfinityException as e:
            test.message = e.message
            sys.stderr.write(e.message + "\n")
            inflogging.log(e.message, "ERROR")
            errors.append(test)
        else:
            passed.append(test)

        test.tear_down()

    base.clean_all()

    if verbose:
        print "FAILED:", len(failed)
        for fail in failed:
            if fail.message:
                print fail.message
        print "ERRORS:", len(errors)
        print "PASSED:", len(passed)


def main():
    signal.signal(signal.SIGINT, sigint_signal)
    signal.signal(signal.SIGTERM, sigint_signal)

    parser = argparse.ArgumentParser(description="Program for running automatic GUI tests.")
    parser.add_argument("-c", "--config", default="/etc/infinity.cfg",
                        help="path to infinity config file (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="store_true", help="print all messages")
    parser.add_argument("directory", default=".", nargs="?", help="directory with tests to run (default: %(default)s)")
    args = parser.parse_args()
    config = load_config(args.config)
    run(args.directory, config, args.verbose)


if __name__ == "__main__":
    main()