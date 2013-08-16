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

import mimetypes
import ConfigParser
import os
import re

from xpresserng.errors import XpresserngError
from xpresserng.image import Image


CLICK_POSITION_RE = re.compile(r"^\s*(?P<x>[-+][0-9]+)\s+(?P<y>[-+][0-9]+)\s*$")


class ImageDirError(XpresserngError):
    """Error related to the image directory."""


class ImageDir(object):
    """Represents a directory with data about images.

    This class doesn't know about any details regarding the images
    themselves, besides the existence of the file in which they reside.
    It will give access to generic ImageData objects containing the
    details about these images.  It's up to an ImageLoader to make sense
    of the actual image data contained in the image files.
    """

    def __init__(self):
        self._images = {}

    def get(self, image_name):
        return self._images.get(image_name)

    def load(self, dirname):
        """Load image information from C{dirname}.

        @param dirname: Path of directory containing xpresserng.ini.
        """
        loaded_filenames = set()
        ini_filename = os.path.join(dirname, "images.cfg")
        if os.path.exists(ini_filename):
            config = ConfigParser.ConfigParser()
            config.read(ini_filename)
            for section_name in config.sections():
                if section_name.startswith("image "):
                    image_name = section_name.split(None, 1)[1]
                    try:
                        image_filename = config.get(section_name, "filename")
                    except ConfigParser.NoOptionError:
                        raise ImageDirError("Image %s missing filename option"
                                            % image_name)
                    image_filename = os.path.join(dirname, image_filename)
                    if not os.path.exists(image_filename):
                        raise ImageDirError("Image %s file not found: %s" %
                                            (image_name, image_filename))
                    try:
                        image_similarity = config.getfloat(section_name,
                                                           "similarity")
                    except ConfigParser.NoOptionError:
                        image_similarity = None
                    except ValueError:
                        value = config.get(section_name, "similarity")
                        raise ImageDirError("Image %s has bad similarity: %s"
                                            % (image_name, value))

                    try:
                        value = config.get(section_name, "focus_delta")
                        match = CLICK_POSITION_RE.match(value)
                        if not match:
                            raise ImageDirError("Image %s has invalid click "
                                                "position: %s" %
                                                (image_name, value))
                        image_focus_delta = (int(match.group("x")),
                                             int(match.group("y")))
                    except ConfigParser.NoOptionError:
                        image_focus_delta = None
                    image = Image(name=image_name,
                                  filename=image_filename,
                                  similarity=image_similarity,
                                  focus_delta=image_focus_delta)
                    self._images[image_name] = image
                    loaded_filenames.add(image_filename)

        # Load any other images implicitly with the default arguments.
        for basename in os.listdir(dirname):
            filename = os.path.join(dirname, basename)
            if filename not in loaded_filenames:
                ftype, fencoding = mimetypes.guess_type(filename)
                if ftype and ftype.startswith("image/"):
                    image_name = os.path.splitext(basename)[0]
                    self._images[image_name] = Image(name=image_name,
                                                     filename=filename)
