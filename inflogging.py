import logging
import datetime
import os

COMPLETE_LOGS = os.path.join(LOG_DIRECTORY, "complete_logs")
CURRENT_LOGDIR = None
TEST_LOGFILE = None
TEST_START_TIME = None


def setup_logging():
    global COMPLETE_LOGS, CURRENT_LOGDIR
    if not os.path.exists(LOG_DIRECTORY):
        os.mkdir(LOG_DIRECTORY)
    if not os.path.exists(COMPLETE_LOGS):
        os.mkdir(COMPLETE_LOGS)
    logging.basicConfig(filename=os.path.join(COMPLETE_LOGS, datetime.datetime.now().isoformat() + '.log'),
                        level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")
    CURRENT_LOGDIR = os.path.join(LOG_DIRECTORY, datetime.datetime.now().isoformat())
    os.mkdir(CURRENT_LOGDIR)


def create_test_logs(test_number):
    # touch log filel
    global CURRENT_LOGDIR, TEST_LOGFILE, TEST_START_TIME
    if not CURRENT_LOGDIR:
        setup_logging()
    TEST_LOGFILE = os.path.join(CURRENT_LOGDIR, "test_%(testnum)03d.log" % {'testnum': test_number})
    TEST_START_TIME = datetime.datetime.now()
    filename = open(TEST_LOGFILE, "a")
    filename.close()


def log(log_message, log_level):
    global TEST_LOGFILE, TEST_START_TIME
    if not TEST_LOGFILE:
        logging.error("log file not set")
        return
    time_from_beggining = str(datetime.datetime.now() - TEST_START_TIME)
    if log_level == "ERROR":
        logging.error(time_from_beggining + ": " + log_message)
        with open(TEST_LOGFILE, "a") as f:
            f.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + ":ERROR: " + time_from_beggining + ": " + log_message + "\n")
    elif log_level == "INFO":
        logging.info(time_from_beggining + ": " + log_message)
    else:
        logging.error("not known log_level")