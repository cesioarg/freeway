#!/usr/bin/python
# -*- coding: utf-8 -*-
# cython: language_level=2, boundscheck=False


class NoValidVersion(Exception):
    pass


class VersionZero(Exception):
    pass


class ExceededPaddingVersion(Exception):
    pass


class NoVersionNumber(Exception):
    pass
