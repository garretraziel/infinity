#!/usr/bin/env python

import argparse
import ConfigParser
import importlib
import os
import sys
from v12n import base
from inftest import InfinityTest, InfinityException, InfinityTestException


def load_config(path):
    config = ConfigParser.RawConfigParser()
    config.read(path)
    conf = {
        "connection": "qemu:///system",
        "logs": "/var/log/infinity"
    }
    try:
        conf["connection"] = config.get("general", "conn")  # TODO: do defaults better
        conf["logs"] = config.get("general", "logs")
    except ConfigParser.NoSectionError:
        pass
    return conf


def load_tests(path):
    config = ConfigParser.RawConfigParser()
    config.read(path)

    tests = []
    for section in config.sections():
        name = config.get(section, "name")
        log_subdir = config.get(section, "log")
        record = config.get(section, "record")
        module = config.get(section, "module")
        vm_name = config.get(section, "vm")
        images = config.get(section, "images")

        localmod = importlib.import_module(module + ".main")
        mainfcn = localmod.main

        tests.append(InfinityTest(name, log_subdir, record, mainfcn, vm_name, images))

    return tests


def run_test(test):
    base.build()


def run(path, config):
    failed = []
    passed = []
    errors = []
    sys.path.insert(0, path)
    tests = load_tests(os.path.join(path, "inftests.cfg"))

    for test in tests:
        try:
            run_test(test)
        except InfinityTestException as e:
            sys.stderr.write(e.message+"\n")
            failed.append(test)
        except InfinityException as e:
            sys.stderr.write(e.message+"\n")
            errors.append(test)
        except Exception as e:
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