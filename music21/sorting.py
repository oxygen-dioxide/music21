# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         sorting.py
# Purpose:      Music21 class for sorting
#
# Authors:      Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2014-2015 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
This module defines a single class, SortTuple, which is a named tuple that can
sort against bare offsets and other SortTuples.

This is a performance-critical object.

It also defines three singleton instances of the SortTupleLow class as ZeroSortTupleDefault,
ZeroSortTupleLow and
ZeroSortTupleHigh which are sortTuple at
offset 0.0, priority [0, -inf, inf] respectively:

>>> sorting.ZeroSortTupleDefault
SortTuple(atEnd=0, offset=0.0, priority=0, classSortOrder=0, isNotGrace=1, insertIndex=0)
>>> sorting.ZeroSortTupleLow
SortTuple(atEnd=0, offset=0.0, priority=-inf, classSortOrder=0, isNotGrace=1, insertIndex=0)
>>> sorting.ZeroSortTupleHigh
SortTuple(atEnd=0, offset=0.0, priority=inf, classSortOrder=0, isNotGrace=1, insertIndex=0)
'''
from __future__ import annotations

from collections import namedtuple
from math import inf as INFINITY
from music21 import exceptions21


class SortingException(exceptions21.Music21Exception):
    pass


class SortTuple(namedtuple('SortTuple', (
    'atEnd', 'offset', 'priority', 'classSortOrder', 'isNotGrace', 'insertIndex'
))):
    '''
    Derived class of namedTuple which allows for comparisons with pure ints/fractions.

    >>> n = note.Note()
    >>> s = stream.Stream()
    >>> s.insert(4, n)
    >>> st = n.sortTuple()
    >>> st
    SortTuple(atEnd=0, offset=4.0, priority=0, classSortOrder=20, isNotGrace=1, insertIndex=...)
    >>> st.shortRepr()
    '4.0 <0.20...>'
    >>> st.atEnd
    0
    >>> st.offset
    4.0

    >>> st < 5.0
    True
    >>> 5.0 > st
    True
    >>> st > 3.0
    True
    >>> 3.0 < st
    True

    >>> st == 4.0
    True

    >>> ts = bar.Barline('double')
    >>> s2 = stream.Stream()
    >>> s2.storeAtEnd(ts)
    >>> ts_st = ts.sortTuple()
    >>> ts_st
    SortTuple(atEnd=1, offset=0.0, priority=0, classSortOrder=-5, isNotGrace=1, insertIndex=...)
    >>> st < ts_st
    True
    >>> ts_st > 999999
    True
    >>> import math
    >>> ts_st == math.inf
    True

    Construct one w/ keywords:

    >>> st = sorting.SortTuple(atEnd=0, offset=1.0, priority=0, classSortOrder=20,
    ...           isNotGrace=1, insertIndex=323)
    >>> st.shortRepr()
    '1.0 <0.20.323>'

    or as tuple:

    >>> st = sorting.SortTuple(0, 1.0, 0, 20, 1, 323)
    >>> st.shortRepr()
    '1.0 <0.20.323>'

    '''
    def __new__(cls, *tupEls, **keywords):
        # noinspection PyTypeChecker
        return super(SortTuple, cls).__new__(cls, *tupEls, **keywords)

    def __eq__(self, other):
        if isinstance(other, tuple):
            return super().__eq__(other)
        try:
            if self.atEnd == 1 and other != INFINITY:
                return False
            elif self.atEnd == 1:
                return True
            else:
                return self.offset == other
        except ValueError:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, tuple):
            return super().__lt__(other)
        try:
            if self.atEnd == 1:
                return False
            else:
                return self.offset < other
        except ValueError:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, tuple):
            return super().__gt__(other)
        try:
            if self.atEnd == 1 and other != INFINITY:
                return True
            elif self.atEnd == 1:
                return False
            else:
                return self.offset > other
        except ValueError:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def shortRepr(self):
        '''
        Returns a nice representation of a SortTuple

        >>> st = sorting.SortTuple(atEnd=0, offset=1.0, priority=0, classSortOrder=20,
        ...           isNotGrace=1, insertIndex=323)
        >>> st.shortRepr()
        '1.0 <0.20.323>'

        >>> st = sorting.SortTuple(atEnd=1, offset=1.0, priority=4, classSortOrder=7,
        ...           isNotGrace=0, insertIndex=200)
        >>> st.shortRepr()
        'End <4.7.[Grace].200>'
        '''
        reprParts = []
        if self.atEnd:
            reprParts.append('End')
        else:
            reprParts.append(str(self.offset))
        reprParts.append(' <')
        reprParts.append(str(self.priority))
        reprParts.append('.')
        reprParts.append(str(self.classSortOrder))

        if self.isNotGrace == 0:
            reprParts.append('.[Grace]')
        reprParts.append('.')
        reprParts.append(str(self.insertIndex))
        reprParts.append('>')
        return ''.join(reprParts)

    def modify(self, **keywords):
        '''
        return a new SortTuple identical to the previous, except with
        the given keyword modified.  Works only with keywords.

        >>> st = sorting.SortTuple(atEnd=0, offset=1.0, priority=0, classSortOrder=20,
        ...           isNotGrace=1, insertIndex=32)
        >>> st2 = st.modify(offset=2.0)
        >>> st2.shortRepr()
        '2.0 <0.20.32>'
        >>> st2
        SortTuple(atEnd=0, offset=2.0, priority=0, classSortOrder=20, isNotGrace=1, insertIndex=32)

        >>> st3 = st2.modify(atEnd=1, isNotGrace=0)
        >>> st3.shortRepr()
        'End <0.20.[Grace].32>'

        The original tuple is never modified (hence tuple):

        >>> st.offset
        1.0

        Changing offset, but nothing else, helps in creating .flatten() positions.
        '''
        # _fields are the namedtuple attributes
        outList = [keywords.get(attr, getattr(self, attr)) for attr in self._fields]
        return self.__class__(*outList)

    def add(self, other):
        '''
        Add all attributes from one sortTuple to another,
        returning a new one.

        >>> n = note.Note()
        >>> n.offset = 10
        >>> s = stream.Stream()
        >>> s.offset = 10
        >>> n.sortTuple()
        SortTuple(atEnd=0, offset=10.0, priority=0, classSortOrder=20, isNotGrace=1, insertIndex=0)
        >>> s.sortTuple()
        SortTuple(atEnd=0, offset=10.0, priority=0, classSortOrder=-20, isNotGrace=1, insertIndex=0)
        >>> s.sortTuple().add(n.sortTuple())
        SortTuple(atEnd=0, offset=20.0, priority=0, classSortOrder=0, isNotGrace=1, insertIndex=0)

        Note that atEnd and isNotGrace are equal to other's value. are upper bounded at 1 and
        take the maxValue of either.
        '''
        if not isinstance(other, self.__class__):
            raise SortingException('Cannot add attributes from a different class')

        outList = [max(getattr(self, attr), getattr(other, attr))
                    if attr in ('atEnd', 'isNotGrace')
                    else (getattr(self, attr) + getattr(other, attr))
                    for attr in self._fields]  # _fields are the namedtuple attributes

        return self.__class__(*outList)

    def sub(self, other):
        '''
        Subtract all attributes from to another.  atEnd and isNotGrace take the min value of either.

        >>> n = note.Note()
        >>> n.offset = 10
        >>> s = stream.Stream()
        >>> s.offset = 10
        >>> n.sortTuple()
        SortTuple(atEnd=0, offset=10.0, priority=0, classSortOrder=20, isNotGrace=1, insertIndex=0)
        >>> s.sortTuple()
        SortTuple(atEnd=0, offset=10.0, priority=0, classSortOrder=-20, isNotGrace=1, insertIndex=0)
        >>> s.sortTuple().sub(n.sortTuple())
        SortTuple(atEnd=0, offset=0.0, priority=0, classSortOrder=-40, isNotGrace=1, insertIndex=0)

        Note that atEnd and isNotGrace are lower bounded at 0.
        '''
        if not isinstance(other, self.__class__):
            raise SortingException('Cannot add attributes from a different class')

        outList = [min(getattr(self, attr), getattr(other, attr))
                    if attr in ('atEnd', 'isNotGrace')
                    else (getattr(self, attr) - getattr(other, attr))
                    for attr in self._fields]  # _fields are the namedtuple attributes

        return self.__class__(*outList)


ZeroSortTupleDefault = SortTuple(atEnd=0, offset=0.0, priority=0, classSortOrder=0,
                                 isNotGrace=1, insertIndex=0)

ZeroSortTupleLow = SortTuple(atEnd=0, offset=0.0, priority=-INFINITY, classSortOrder=0,
                             isNotGrace=1, insertIndex=0)

ZeroSortTupleHigh = SortTuple(atEnd=0, offset=0.0, priority=INFINITY, classSortOrder=0,
                              isNotGrace=1, insertIndex=0)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import music21
    music21.mainTest()
