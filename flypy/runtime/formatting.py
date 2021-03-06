# -*- coding: utf-8 -*-

"""
String formatting functionality for some primitive types. We do this since
it depends on several object implementations at once (e.g. Buffer and String),
which themselves need say, integers.
"""

from __future__ import print_function, division, absolute_import
import math

import flypy.types
from flypy import jit

#===------------------------------------------------------------------===
# Formatters
#===------------------------------------------------------------------===

@jit
def sprintf(buf, fmt, x):
    """
    Print `x` to `buf` according to `format`.

    Returns the number of characters written.
    """
    fmt = flypy.runtime.obj.core.as_cstring(fmt)
    n = len(buf)
    result = flypy.libc.snprintf(buf.pointer(), n, fmt, x)
    #if result >= n:
    #    raise ValueError("Unable to print to buffer:")
    return result + 1 # n bytes + '\0

@jit
def format_static(fmt, x, n):
    """
    Format 'x' according to 'fmt' using a static buffer size 'n'.

        - upcast to a double
        - use snprintf
        - resize buffer according to # of bytes written
    """
    buf = flypy.runtime.obj.core.newbuffer(flypy.types.char, n)
    n = sprintf(buf, fmt, x)
    buf.resize(n)
    return flypy.types.String(buf)
