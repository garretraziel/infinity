import logging
import datetime
import os
from infexceptions import InfinityException

LOG_DIRECTORY = None
COMPLETE_LOGS = None
CURRENT_LOGDIR = None
TEST_LOGFILE = None
TEST_START_TIME = None


class LoggingOutput(object):
    def __init__(self, output, verbose, prefix, err=False):
        self.output = output
        self.verbose = verbose
        self.err = err
        self.prefix = prefix
        self.in_test = False

    def write(self, buf):
        message = str(self.prefix) + ": " + buf
        #self.log(message)

        if self.verbose or self.err:
            self.output.write(message)

        if self.in_test:
            global TEST_LOGFILE, TEST_START_TIME
            time_passed = str(datetime.datetime.now() - TEST_START_TIME)

            with open(TEST_LOGFILE, "a") as f:
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " at " + time_passed + ":" + message)

    def log(self, message):
        global TEST_LOGFILE, TEST_START_TIME
        if not TEST_LOGFILE:
            logging.error("log file not set")
            raise InfinityException("log file not set")
        time_from_beginning = str(datetime.datetime.now() - TEST_START_TIME)
        if self.err:
            logging.error(time_from_beginning + ":" + message)
        else:
            logging.info(time_from_beginning + ":" + message)


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


def create_test_logs(test_name):
    # touch log filel
    global CURRENT_LOGDIR, TEST_LOGFILE, TEST_START_TIME
    if not CURRENT_LOGDIR:
        raise InfinityException("logging was not configured")
    nameify = test_name.lower().replace(" ", "_")
    TEST_LOGFILE = os.path.join(CURRENT_LOGDIR, nameify)
    TEST_START_TIME = datetime.datetime.now()
    filename = open(TEST_LOGFILE, "a")
    filename.close()