#!/usr/bin/env python

import argparse


def load_config(path):
    pass


def run(path, config):
    pass


def main():
    parser = argparse.ArgumentParser(description="Program for running automatic GUI tests.")
    parser.add_argument("-c", "--config", default="/etc/infinity.cfg",
                        help="path to infinity config file (default: %(default)s)")
    parser.add_argument("directory", default=".", nargs="?", help="directory with tests to run (default: %(default)s)")
    args = parser.parse_args()
    config = load_config(args.config)
    run(args.directory, config)


if __name__ == "__main__":
    main()