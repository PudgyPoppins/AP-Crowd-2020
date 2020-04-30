# -*- coding: utf-8 -*-
from .extension import BleachExtension


VERSION = '0.1.4'


def makeExtension(**kwargs):
    return BleachExtension(**kwargs)
