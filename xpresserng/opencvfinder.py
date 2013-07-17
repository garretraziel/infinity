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

#TODO: is find_all for anything usable?
#TODO: make find_all

import cv2
from xpresserng.imagematch import ImageMatch
import logging


class OpenCVFinder(object):
    def find(self, screen_image, area_image):
        resultloc, resultval = self._find(screen_image, area_image)
        if resultloc is None or resultval is None:
            return None
        else:
            return ImageMatch(area_image, resultloc[0], resultloc[1], resultval)

    def _load_image(self, image):
        if "opencv_image" not in image.cache:
            if image.filename is not None:
                opencv_image = cv2.imread(image.filename)
            elif image.array is not None:
                opencv_image = image.array
            else:
                raise RuntimeError("Oops. Can't load image.")
            image.cache["opencv_image"] = opencv_image
            image.width = len(opencv_image[0])
            image.height = len(opencv_image)
        return image.cache["opencv_image"]

    def _find(self, screen_image, area_image):
        source = self._load_image(screen_image)
        template = self._load_image(area_image)
        if len(source) <= 400 and len(source[0]) <= 720:
            logging.debug("skipping broken image")
            return None, None
        try:
            match = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
        except: # because of opencv assertion error (matrix.cpp:115)
            return None, None
        # do I have to normalize?
        minval, maxval, minloc, maxloc = cv2.minMaxLoc(match)
        if area_image.similarity <= maxval:
            return maxloc, maxval
        else:
            return None, None