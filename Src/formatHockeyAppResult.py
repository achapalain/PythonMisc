#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Framework.stringOperations import *

class LineDesc:
    def __init__(self, index=-1, text=""):
        self.index = index
        self.text = text
        while self.text.endswith(" ") or self.text.endswith("\t"):
            self.text = self.text[:-1]
        self.cleanedText = text.replace("\t", "")
        while self.cleanedText.startswith(" "):
            self.cleanedText = self.cleanedText[1:]
        self.isEmpty = self.text == ""
        self.lastChar = self.text[-1] if len(self.text) > 0 else ""
        self.firstChar = self.cleanedText[0] if len(self.cleanedText) > 0 else ""

def toLinesDesc(lines):
    return [LineDesc(i, line) for i, line in enumerate(lines)]

def toIndexedContent(lines):
    res = []
    for i, line in enumerate(lines):
        res.append((i, line))
    return res

def parseFile(inputFile, outputFile):
    lines = textToLines(inputFile)
    return parseText(lines)

def parseText(text, outputFile=None):
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    if isinstance(text, str):
        text = textToLines(text)

    linesDesc = toLinesDesc(text)
    res = []
    for i in range(int(len(linesDesc) / 4)):
        sub = linesDesc[i * 4 : i * 4 + 4]
        sub = [x.text for x in sub]
        sub = "\t".join(sub)
        sub = sub.replace("<color=white>[Save]</color> : ReadSaveInfo ", "")
        sub = sub.replace(".dat", "")
        sub = sub.replace(" context: ", "\t")
        sub = sub.replace(" details: ", "\t")
        sub = sub.replace(" details:", "\t")
        sub = sub.split("\t")
        for j in [9, 8, 4, 1, 0]:
            sub.pop(j)
        res.append("\t".join(sub))

    res = "\n".join(res)
    print(res)

    if outputFile:
        with open(outputFile, "w") as outFile:
            outFile.writelines(res)

    return res

if __name__ == "__main__":
    #inputFile = "C:/Ohbibi/Git/Sup/Unity/Assets/Scripts/Managers/SocialManager.cs"
    #outputFile = inputFile
    #parseFile(inputFile, outputFile)
    res = common.waitForText("Enter text to be formated:")
    if res == "":
        res = common.Clipboard.get()
    res = parseText(res)
    common.Clipboard.set(res)


