#!/usr/bin/env python

import argparse
import ConfigParser
import importlib
import os
import sys
import inflogging
from v12n import base
from xpresserng import Xpresserng
from inftest import InfinityTest, InfinityException, InfinityTestException


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
    config.read(os.path.join(path, "inftests.cfg"))

    tests = []
    for section in config.sections():
        name = config.get(section, "name")
        log_subdir = config.get(section, "log")
        record = config.get(section, "record")
        module = config.get(section, "module")
        vm_xml_file = config.get(section, "vm")
        xml_file = open(os.path.join(path, vm_xml_file))
        vm_xml = xml_file.read()
        xml_file.close()
        images = os.path.join(path, config.get(section, "images"))

        try:
            imported_module = importlib.import_module(module + ".main")
            main = imported_module.main
        except ImportError:
            raise InfinityException("Test module "+module+" cannot be imported.")

        tests.append(InfinityTest(name, log_subdir, record, main, vm_xml, images))

    return tests


def run_test(test):
    inflogging.create_test_logs(test.name)
    test.vm = base.build(test.vm_xml)
    xpng = Xpresserng()


def run(path, config):
    failed = []
    passed = []
    errors = []
    sys.path.insert(0, path)
    tests = load_tests(path)
    inflogging.setup_logging(config["logs"])
    base.setup_v12n(config["connection"], config["pool"])

    for test in tests:
        try:
            run_test(test)
        except InfinityTestException as e:
            test.message = e.message
            if config.verbose:
                sys.stderr.write(e.message+"\n")
            failed.append(test)
        except InfinityException as e:
            test.message = e.message
            sys.stderr.write(e.message+"\n")
            errors.append(test)
        except Exception as e:
            test.message = e.message
            sys.stderr.write(e.message+"\n")
            errors.append(test)
        else:
            passed.append(test)

    if config.verbose:
        print "FAILED:", len(failed)
        for fail in failed:
            if fail.message:
                print fail.message
        print "ERRORS:", len(errors)
        print "PASSED:", len(passed)


def main():
    parser = argparse.ArgumentParser(description="Program for running automatic GUI tests.")
    parser.add_argument("-c", "--config", default="/etc/infinity.cfg",
                        help="path to infinity config file (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="store_true", help="print all messages")
    parser.add_argument("directory", default=".", nargs="?", help="directory with tests to run (default: %(default)s)")
    args = parser.parse_args()
    config = load_config(args.config)
    run(args.directory, config)


if __name__ == "__main__":
    main()