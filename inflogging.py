import logging
import datetime
import os
import string
import sys
from infexceptions import InfinityException

LOG_DIRECTORY = None
COMPLETE_LOGS = None
CURRENT_LOGDIR = None
TEST_LOGFILE = None
TEST_START_TIME = None

ORIG_STDOUT = sys.stdout
ORIG_STDERR = sys.stderr


FAIL = '\033[91m'
ENDC = '\033[0m'


class LoggingOutput(object):
    def __init__(self, output, verbose, prefix, err=False):
        self.output = output
        self.verbose = verbose
        self.err = err
        self.prefix = prefix
        self.in_test = False
        self.newline = True
        self.old_msg = ""

    def write(self, buf):
        global ORIG_STDERR, FAIL, ENDC
        stderr_handler = sys.stderr
        sys.stderr = ORIG_STDERR

        if self.newline:
            message = str(self.prefix) + ": " + buf
        else:
            message = buf

        self.old_msg += message

        if self.verbose or self.err:
            if self.output.isatty() and self.err:
                self.output.write(FAIL+message+ENDC)
            else:
                self.output.write(message)

        if self.in_test:
            global TEST_LOGFILE, TEST_START_TIME
            time_passed = str(datetime.datetime.now() - TEST_START_TIME)

            with open(TEST_LOGFILE, "a") as f:
                if self.newline:
                    m = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " at " + time_passed + ":" + message
                else:
                    m = message
                f.write(m)

        if buf[-1] == "\n":
            self.newline = True
            self.log(self.old_msg[:-1])
            self.old_msg = ""
        else:
            self.newline = False

        sys.stderr = stderr_handler

    def log(self, message):
        if self.err:
            logging.error(message)
        else:
            logging.info(message)


def setup_logging(path):
    global COMPLETE_LOGS, CURRENT_LOGDIR, LOG_DIRECTORY

    if not LOG_DIRECTORY:
        LOG_DIRECTORY = path
    if not COMPLETE_LOGS:
        COMPLETE_LOGS = os.path.join(path, "complete_logs")

    if not os.path.exists(LOG_DIRECTORY):
        os.mkdir(LOG_DIRECTORY)
    if not os.path.exists(COMPLETE_LOGS):
        os.mkdir(COMPLETE_LOGS)

    now = datetime.datetime.now().isoformat()
    complete_log = os.path.join(COMPLETE_LOGS, now + '.log')
    logging.basicConfig(filename=complete_log, level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")

    CURRENT_LOGDIR = os.path.join(LOG_DIRECTORY, now)
    os.mkdir(CURRENT_LOGDIR)

    try:
        os.remove(os.path.join(path, "latest"))
    except OSError:
        pass

    try:
        os.symlink(CURRENT_LOGDIR, os.path.join(path, "latest"))
    except OSError:
        pass

    try:
        os.remove(os.path.join(COMPLETE_LOGS, "latest"))
    except OSError:
        pass

    try:
        os.symlink(complete_log, os.path.join(COMPLETE_LOGS, "latest"))
    except OSError:
        pass


def nameify(ugly_name):
    from_str = " /&*\\"
    to_str = "_"*len(from_str)
    transtable = string.maketrans(from_str, to_str)
    return ugly_name.lower().translate(transtable)


def create_test_logs(test_name):
    # touch log filel
    global CURRENT_LOGDIR, TEST_LOGFILE, TEST_START_TIME
    if not CURRENT_LOGDIR:
        raise InfinityException("logging was not configured")

    pretty_name = nameify(test_name)
    TEST_LOGFILE = os.path.join(CURRENT_LOGDIR, pretty_name)
    TEST_START_TIME = datetime.datetime.now()
    filename = open(TEST_LOGFILE, "a")
    filename.close()