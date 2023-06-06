#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re

def removeWhiteSpaces(txt):
    for v in ["\t", "\n", "\r", " ", " "]:
        txt = txt.replace(v, "")
    return txt

def getNumber(val, decimalChar=".", thousandChar=""):
    val = removeWhiteSpaces(val)
    val = val.replace(thousandChar, "")
    val = val.replace(decimalChar, ".")
    val = re.search("([\d.]*)", val)
    if val:
        val = val.group(1)
        if val != "" and val != ".":
            if val.find(".") >= 0:
                return float(val)
            else:
                return int(val)

def getBool(data):
    if isinstance(data, bool):
        return data
    elif isinstance(data, str):
        data = removeWhiteSpaces(data).upper()
        if data in ["1", "TRUE", "YES", "OUI"]:
            return True
        elif data in ["0", "FALSE", "NO", "NONE", "NON"]:
            return False



def split_texts(text, *separators):
    res = []
    start = text.find(separators[0])
    if start < 0:
        return res
    for i in range(1, len(separators)):
        sep = separators[i]
        end = text.find(sep, start)
        if end < 0:
            res.append(text[start:])
            return res
        else:
            res.append(text[start:end])
            start = end
    res.append(text[start:])
    return res


class TextProc():
    def __init__(self, data=""):
        self.text = data
        self.cursorStart = -1
        self.cursorEnd = -1

    def locate(self, text):
        self.cursorStart = self.text.find(text)
        self.cursorEnd = self.cursorStart + len(text) if self.cursorStart >= 0 else -1
        return self

    def locateBrackets(self, leftBracket, rightBracket):
        self.cursorStart = self.text.find(leftBracket)
        if self.cursorStart >= 0:
            self.cursorEnd = self.text.find(rightBracket, self.cursorStart + len(leftBracket))
            self.cursorEnd += len(rightBracket)
        return self

    def locateBracketsContent(self, leftBracket, rightBracket):
        self.locateBrackets(leftBracket, rightBracket)
        self.cursorStart += len(leftBracket)
        self.cursorEnd -= len(rightBracket)
        return self

    def getBrackets(self, leftBracket, rightBracket):
        return self.locateBrackets(leftBracket, rightBracket).center()

    def getBracketsContent(self, leftBracket, rightBracket):
        return self.locateBracketsContent(leftBracket, rightBracket).center()

    def left(self):
        if self.cursorStart >= 0:
            return TextProc(self.text[0: self.cursorStart])
        return TextProc()
        
    def center(self):
        if self.cursorStart >= 0 and self.cursorEnd >= 0:
            return TextProc(self.text[self.cursorStart: self.cursorEnd])
        return TextProc()

    def right(self):
        if self.cursorEnd >= 0:
            return TextProc(self.text[self.cursorEnd:])
        return TextProc()

    def strip(self, stripper=[" "]):
        if isinstance(stripper, str):
            stripper = [stripper]
        data = self.text
        for s in stripper:
            data = data.strip(s)
        return TextProc(data)

    def getValue(self):
        return self.text
    
    def getNumber(self, decimalChar=".", thousandChar=""):
        return getNumber(self.text, decimalChar, thousandChar)

    def getBool(self):
        return getBool(self.text)
    
