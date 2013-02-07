
"""
io_utils
========

Utilities related to IO and printing.
"""

import time

def format_time_if_defined(time_format, time_tuple):
    """
    Return a string representation of a possibly undefined time.

    Jobs may have an undefined start time, for example, if they
    have not started running yet. This method is just an extension
    of `time.strftime` which returns an empty string if the `time`
    argument is None.

    :Examples:
        >>> format_time_if_defined('%c',time.gmtime())
        'Thu Feb  7 17:07:11 2013'
        >>> format_time_if_defined('%c',None)
        ''

    """
    try:
        return time.strftime(time_format, time_tuple)
    except TypeError:
        return ""

