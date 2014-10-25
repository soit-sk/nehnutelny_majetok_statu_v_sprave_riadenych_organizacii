#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debugging and helper stuff for this scraper.
"""


DEBUG = False
COLOR = '\033[92m'
ENDCOLOR = '\033[0m'

def prt(text):
    if DEBUG:
        print ''.join((COLOR, repr(text), ENDCOLOR))

