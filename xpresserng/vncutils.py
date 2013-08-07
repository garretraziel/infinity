# (c) Jan Sedlak, Red Hat
import cv2

import types
import os
import logging
import time

from image import Image
from tempfile import NamedTemporaryFile

ABSPATH = os.path.dirname(os.path.abspath(__file__))

from vncdotool import api
from vncdotool.client import KEYMAP


def to_special(string):
    """Return 'special' for '<special>' if 'special' is KEYMAP word, otherwise None.

    >>> to_special("<enter>")
    'enter'
    >>> to_special("<foobar>")
    >>> to_special("foobar")

    """
    if string.startswith("<") and string.endswith(">") and string[1:-1] in KEYMAP:
        return string[1:-1]
    else:
        return None


def key_argument_type(argument):
    """Return type argument for VNC typing.

    Return "MULTIKEYS" when argument is correct list of keys to type,
    return "SPECIAL" if argument is string with one key from KEYMAP,
    return "KEYS" if argument is normal string with keys to type and
    return "FAIL" otherwise.

    >>> key_argument_type("foobar")
    'KEYS'
    >>> key_argument_type("<enter>")
    'SPECIAL'
    >>> key_argument_type(["<ctrl>", "<alt>", "<del>"])
    'MULTIKEYS'
    >>> key_argument_type(["<ctrl>", "s"])
    'MULTIKEYS'
    >>> key_argument_type(["f", "o", "o"])
    'FAIL'
    >>> key_argument_type("<foobar>")
    'KEYS'
    >>> key_argument_type(4)
    'FAIL'

    """
    if isinstance(argument, types.ListType):
        for item in argument[:-1]:  # last one can be normal key, others have to be special
            if not to_special(item):
                return "FAIL"
        if len(argument[-1]) > 1 and not to_special(argument[-1]):  # last one should be only one key
            return "FAIL"
        else:
            return "MULTIKEYS"
    elif isinstance(argument, types.StringType):
        if to_special(argument):
            return "SPECIAL"
        else:
            return "KEYS"
    else:
        return "FAIL"


class VncTool(object):
    """Class for controlling target machine via VNC.

    It provides methods for typing on keyboard, clicking with mouse and
    screenshotting desktop.
    """

    def __init__(self, host, port, password):
        """Initialize VncTool with host, port and password for VNC it will use."""
        #TODO: TBD password usage
        self.host = host
        self.password = password
        self.port = port
        self.client = api.connect(":".join([host, str(port-5900)]))  # TODO: toto je hroznej sranec, oh muj boze

    def click(self, x, y):
        """Click on given coordinates with mouse."""
        self.client.mouseMove(x, y)
        self.client.mousePress(1)

    def right_click(self, x, y):
        """Rightclick on given coordinates with mouse."""
        self.client.mouseMove(x, y)
        self.client.mousePress(3)

    def double_click(self, x, y):
        """Doubleclick on given coordinates with mouse."""
        self.client.mouseMove(x, y)
        self.client.mousePress(1)
        time.sleep(0.1)
        self.client.mousePress(1)

    def hover(self, x, y):
        """Move mouse to given coordinates."""
        self.client.mouseMove(x, y)

    def keyboard_type(self, string):
        """Type given keys on keyboard on target machine.

        String argument doesn't have to be only "string" type.
        When called with simple string, it types all characters
        given in this string. If string starts with "<" character
        and ends with ">" and between "<" and ">" is word from
        KEYWORDS list, type that special key. If argument is list,
        of strings, press all those keys together. Note that when
        called with list, every item except the last one should be
        special key. Last one can be special key or one character.
        See key_argument_type function for reference.

        """
        arg_type = key_argument_type(string)
        if arg_type == "MULTIKEYS":
            keys = [to_special(key) for key in string[:-1]]  # convert special keys to KEYMAP
            last_key = to_special(string[-1])  # try to convert the last one
            if last_key:  # last one is special key
                keys.append(last_key)
            else:  # last one is normal character
                keys.append(string[-1])
            keys = "-".join(keys)  # vncdotool expects it that way
            self.__type_key(keys)
        elif arg_type == "SPECIAL":
            key = to_special(string)
            self.__type_key(key)
        elif arg_type == "KEYS":
            self.__type_standard(string)
        else:
            print "#ERROR: unknown argument type for keyboard_type function."

    def __type_standard(self, string):
        """Send command to type standard keys over VNC."""
        for char in string:
            self.client.keyPress(char)  # TODO: rather string than keystrokes
            time.sleep(0.1)

    def __type_key(self, keys):
        """Send commant to type special keys over VNC."""
        self.client.keyPress(keys)

    def take_screenshot(self, debug=True):
        """Take screenshot of desktop and return name of file where was it saved."""
        with NamedTemporaryFile(prefix='xpresserng_', suffix='.png', delete=not debug) as f:
            self.client.captureScreen(f.name)
            opencv_image = cv2.imread(f.name)
        return Image("screenshot", array=opencv_image,
                     width=len(opencv_image[0]), height=len(opencv_image))

    def log_vm(self, screenshot_name):
        self.client.captureScreen(screenshot_name)
        # perhaps image of VM RAM?
