#!/usr/bin/python
# -*- coding: utf-8 -*-

class NoValidVersion(Exception):
    pass


class VersionZero(Exception):
    pass


class ExceededPaddingVersion(Exception):
    pass


class NoVersionNumber(Exception):
    pass
