#!/usr/bin/env python
# -*- coding: utf-8 -*-

import obbinstall, sys

def getParam(param, defaultValue=None):
    searchedParam = param + "="
    res = defaultValue
    for arg in sys.argv:
        if searchedParam in arg:
            res = arg.replace(searchedParam, "")
            break
    if isinstance(res, str) and defaultValue != None:
        if isinstance(defaultValue, bool):
            if res.lower() == "false":  res = False
            elif res.lower() == "true":  res = True
        elif isinstance(defaultValue, int):
            res = int(res)
        elif isinstance(defaultValue, float):
            res = float(res)
    print(param, res)
    return res

def hasParam(param):
    if param in sys.argv:
        return True
