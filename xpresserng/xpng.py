#
# Copyright (c) 2010 Canonical
#
# Written by Gustavo Niemeyer <gustavo@niemeyer.net>
#
# This file is part of the Xpresser GUI automation library.
#
# Xpresser is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3,
# as published by the Free Software Foundation.
#
# Xpresser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# (c) Jan Sedlak, Red Hat

import time
import types
import cv2

from xpresserng.vncutils import VncTool
from xpresserng.errors import XpresserngError
from xpresserng.imagedir import ImageDir
from xpresserng.imagematch import ImageMatch
from xpresserng.opencvfinder import OpenCVFinder


class ImageNotFound(XpresserngError):
    """Exception raised when a request to find an image doesn't succeed."""


class Xpresserng(object):
    def __init__(self, host="127.0.0.1", port=5900, password=None, debug=False):
        self._imagedir = ImageDir()
        self._imagefinder = OpenCVFinder()
        self._vnctool = VncTool(host, port, password)
        self.debug = debug
        self.recording = False

    def load_images(self, path):
        self._imagedir.load(path)

    def get_image(self, name):
        return self._imagedir.get(name)

    def _compute_focus_point(self, args):
        if (len(args) == 2 and
                isinstance(args[0], (int, long)) and
                isinstance(args[1], (int, long))):
            return args
        elif len(args) == 1:
            if type(args[0]) == ImageMatch:
                match = args[0]
            else:
                match = self.find(args[0])
            return match.focus_point

    def set_recording(self, filename):
        try:
            self.recording = True
            self.video_file = filename
            self.video_writer = cv2.VideoWriter(self.video_file, cv2.cv.CV_FOURCC('T', 'H', 'E', 'O'), 2, (1024, 768), True)
        except: # when opencv with theora isn't supported
            self.recording = False

    def click(self, *args):
        """Click on the position specified by the provided arguments.

        The following examples show valid ways of specifying the position:

            xp.click("image-name")
            xp.click(image_match)
            xp.click(x, y)
        """
        self._vnctool.click(*self._compute_focus_point(args))

    def right_click(self, *args):
        """Right-click on the position specified by the provided arguments.

        The following examples show valid ways of specifying the position:

            xp.right_click("image-name")
            xp.right_click(image_match)
            xp.right_click(x, y)
        """
        self._vnctool.right_click(*self._compute_focus_point(args))

    def double_click(self, *args):
        """Double clicks over the position specified by arguments

        The following examples show valid ways of specifying the position:
             xp.double_click("image-name")
             xp.double_click(image_match)
             xp.double_click(x, y)
        """
        self._vnctool.double_click(*self._compute_focus_point(args))

    def hover(self, *args):
        """Hover over the position specified by the provided arguments.

        The following examples show valid ways of specifying the position:

            xp.hover("image-name")
            xp.hover(image_match)
            xp.hover(x, y)
        """
        self._vnctool.hover(*self._compute_focus_point(args))

    def find(self, image, timeout=10):
        """Given an image or an image name, find it on the screen.

        @param image: Image or image name or list of names to be searched for.
        @return: An ImageMatch instance, or None.
        """
        if isinstance(image, basestring):
            image = self._imagedir.get(image)
        if isinstance(image, types.ListType) and isinstance(image[0], basestring):
            for i, im in enumerate(image):
                image[i] = self._imagedir.get(im)
        wait_until = time.time() + timeout
        while time.time() < wait_until:
            screenshot_image = self._vnctool.take_screenshot(debug=self.debug)
            if self.recording:
                if self.video_writer:
                    self.video_writer.write(screenshot_image.array)
            if isinstance(image, types.ListType):
                for im in image:
                    match = self._imagefinder.find(screenshot_image, im)
                    if match is not None:
                        return match
            else:
                match = self._imagefinder.find(screenshot_image, image)
                if match is not None:
                    return match
        raise ImageNotFound(image)

    def wait(self, image, timeout=30):
        """Wait for an image to show up in the screen up to C{timeout} seconds.

        @param image: Image or image name to be searched for.
        @return: An ImageMatch instance, or None.
        """
        self.find(image, timeout)

    def type(self, string):
        """Enter the string provided as if it was typed via the keyboard.

        It can take following arguments:
        string - "qwerty" - type those on keyboard
        special string - "<enter>" - press this special key
        list of special strings, may end with char - press all this keys together.
          Example: ["<control>", "<alt>", "<delete>"], ["<control>", "s"].

        """
        self._vnctool.keyboard_type(string)

    def log_vm(self, screenshot_filename):
        """Log information about virtual machine, save screenshot."""
        self._vnctool.log_vm(screenshot_filename)
