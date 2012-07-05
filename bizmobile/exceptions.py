# -*- coding: utf-8 -*-
"""
Exceptions

:ctime: 2012-06-26T09:02:57
"""


class BizmobileError(Exception):
    """ Bizmobile exception """

    def __init__(self, reason, response=None):
        self.reason = unicode(reason)
        self.response = response

    def __str__(self):
        return self.reason
