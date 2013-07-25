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

DEFAULT_SIMILARITY = 0.98


class Image(object):
    """An image. :-)

    @ivar name: The human-oriented name of this image. May be None.

    @ivar similarity: The similarity tolerance to be used when searching
        for this image.

        Varies between 0.0 and 1.0, where 1.0 is a perfect match.  Defaults
        to the value of DEFAULT_SIMILARITY when not specified in the image
        data.

    @ivar focus_delta: (dx, dy) pair added to the center position to
        find where to click.

        For instance, if the *center* of the image is found at 200, 300 and
        the focus_point is (10, -20) the click will actually happen at the
        screen position (210, 280).

        When not specified, (0, 0) is assumed, which means click in the
        center of the image itself.

    @ivar width: The width of the image.

    @ivar height: The height of the image.

    @ivar filename: Filename of the image.

    @ivar array: Numpy array with three dimensions (rows, columns, RGB).

    @ivar cache: Generic storage for data associated with this image, used
        by the image finder, for instance.
    """

    def __init__(self, name=None, similarity=None, focus_delta=None,
                 width=None, height=None, filename=None, array=None):
        if similarity is None:
            similarity = DEFAULT_SIMILARITY
        if focus_delta is None:
            focus_delta = (0, 0)

        if not (0 < similarity < 1):
            raise ValueError("Similarity out of range: %.2f" % similarity)

        self.name = name
        self.similarity = similarity
        self.focus_delta = focus_delta
        self.width = width
        self.height = height
        self.filename = filename
        self.array = array
        self.cache = {}

    def __str__(self):
        if self.filename:
            return self.filename
        if self.name:
            return self.name
        return "unknown image"

    def __repr__(self):
        return self.__str__()