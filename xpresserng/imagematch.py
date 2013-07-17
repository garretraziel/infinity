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

from xpresserng.errors import XpresserngError


class ImageMatchError(XpresserngError):
    """Error raised due to an ImageMatch related problem (really!)."""
    pass


class ImageMatch(object):
    """An image found inside another image.

    @ivar image: The image found.
    @ivar x: Position in the X axis where the image was found.
    @ivar y: Position in the Y axis where the image was found.
    @ivar similarity: How similar to the original image the match was,
        where 1.0 == 100%.
    @ivar focus_point: The position in the screen which this image match
        represents.  This is useful for clicks, hovering, etc.  If no delta
        was specified in the image data itself, this will map to the center
        of the found image.
    """

    def __init__(self, image, x, y, similarity):
        if image.height is None:
            raise ImageMatchError("Image.height was None when trying to "
                                  "create an ImageMatch with it.")
        if image.width is None:
            raise ImageMatchError("Image.width was None when trying to "
                                  "create an ImageMatch with it.")

        self.image = image
        self.x = x
        self.y = y
        self.similarity = similarity
        self.focus_point = (x + image.width // 2 + image.focus_delta[0],
                            y + image.height // 2 + image.focus_delta[1])
