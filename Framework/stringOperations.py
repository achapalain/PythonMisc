#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, collections, obbinstall, pprint
from os.path import *

def textToLines(text, enc="utf8"):
    '''
    Return a list of lines
    :param text: raw text OR file path of a text file
    '''
    if not text:
        return []
    if len(text) < 256 and os.path.isfile(text):
        with open(text, encoding=enc) as file:
            text = file.read()
    return text.replace("\r\n", "\n").split("\n")

def printIntoFile(path, lines):
     with open(path, "w", encoding="utf8") as f:
         for line in lines:
            f.write(line + "\n")

def replace(lines, searched, replacement, useRegex=False):
    res = []
    if not useRegex:
        for line in lines:
            res.append(line.replace(searched, replacement))
    else:
        searched = re.compile(searched)
        for line in lines:
            res.append(searched.sub(replacement, line))
    return res

def removeEmptyLines(lines):
    res = []
    for line in lines:
        if line.replace(" ", "").replace("\t", "") != "":
            res.append(line)
    return res

def removePattern(lines, pattern):
    """
    Remove a specific regex pattern from all lines
    :param pattern: regex with searched pattern
    """
    res = []
    for i, line in enumerate(lines):
        res = re.findall(pattern, line)
        if res:
            for x in res:
                line = line.replace(x, "")
            res.append(line)
    return res

def removeLinesBlock(lines, blockStart, blockEnd, useRegEx=False, keepStart=False, keepEnd=False):
    res = []
    keepLine = True
    if not useRegEx:
        for line in lines:
            if blockStart in line:
                keepLine = False
                if keepStart:
                    res.append(line)
            if keepLine:
                res.append(line)
            if blockEnd in line:
                keepLine = True
                if keepEnd:
                    res.append(line)
    else:
        blockStart = re.compile(blockStart)
        blockEnd = re.compile(blockEnd)
        for line in lines:
            if blockStart.match(line) is not None:
                keepLine = False
                if keepStart:
                    res.append(line)
            if keepLine:
                res.append(line)
            if blockEnd.match(line) is not None:
                keepLine = True
                if keepEnd:
                    res.append(line)
    return res


def removeCharacters(lines, indexFrom, indexTo):
    '''
    removes all characters between 'From' and 'To' indexes (inclusive)
    (example: removeCharacters(["1235456789"], 2, 4) returns ["16789"]
    :return: lines without specified characters
    '''
    res = []
    if indexFrom > indexTo:
        indexFrom, indexTo = indexTo, indexFrom
    for i, line in enumerate(lines):
        resLine = ""
        if indexFrom > 0 and indexFrom < len(line):
            resLine += line[:indexFrom-1]
        if indexTo > 0 and indexTo < len(line):
            resLine += line[indexTo+1:]
        res.append(resLine)
    return res

def removeLineWithPattern(lines, pattern, useRegex=False):
    res = []
    if not useRegex:
        for line in lines:
            if pattern not in line:
                res.append(line)
    else:
        for i, line in enumerate(lines):
            resSearch = re.findall(pattern, line)
            if not resSearch or len(resSearch) == 0:
                res.append(line)
    return res

def removeLineStartingWith(lines, pattern):
    res = []
    for i, line in enumerate(lines):
        if not line.startswith(pattern):
            res.append(line)
    return res

def removeLineEndingWith(lines, pattern):
    res = []
    for i, line in enumerate(lines):
        if not line.endswith(pattern):
            res.append(line)
    return res

def strip(lines):
    '''
    apply .strip() to all lines
    :return: striped lines
    '''
    res = []
    for line in lines:
        res.append(line.strip())
    return res
    
def getFirstMatch(line, pattern, logErrors=False):
    match = None
    try:
        match = re.findall(pattern, line)[0]
    except IndexError:
        if logErrors:
            print("No match for line: " + line)
    return match

def reorderMatchingPattern(lines, pattern):
    start = None
    for i, line in enumerate(lines):
        if pattern in line and start is None:
            start = i
        elif pattern not in line and start is not None:
            block = lines[start:i]
            block.sort()
            for j in range(start, i):
                lines[j] = block[j-start]
            start = None
    return lines

def isolatePattern(lines, pattern):
    res = []
    for i, line in enumerate(lines):
        subRes = re.findall(pattern, line)
        res += subRes
    return res

def countLines(lines):
    """
    :return: list of (line, count) couples, sorted by count
    """
    trackedLines = {}
    for x in lines:
        if x not in trackedLines:   trackedLines[x] = 1
        else:                       trackedLines[x] += 1
    trackedList = [(x, trackedLines[x]) for x in trackedLines]
    trackedList.sort(key = lambda x: "%10d %s" % (x[1], x[0]), reverse=True)
    return trackedList

def sortLines(lines):
    lines.sort()
    return lines

# Generic content operators, to manipulate array of dictionaries
def createFormattedLines(values, formatter, *fields):
    '''
    TODO: what is this function doing ?
    '''
    res = []
    for x in values:
        values = [x[field] for field in fields]
        res.append(formatter.format(*values))
    return res

# def sortContent(values, sorter):

def checkAccolade(text):
    '''
    TODO: what is this function doing ?
    '''
    lines = textToLines(text)
    for line in lines:
        if '":' not in line:
            continue
        errors = 0
        start = line.find("{0")
        if start != -1 and line[start+2] != "}":
            errors += 1
        start = line.find("0}")
        if start != -1 and line[start-1] != "{":
            errors += 1
        if line.count("{") != line.count("}"):
            errors += 1
        if errors != 0:
            print(errors, line)
            
def getLogPrefix_Android(line, logErrors=False):
    pattern = "[0-9]+-[0-9]+ [0-9]+:[0-9]+:[0-9]+.[0-9]+: [?=WDIAEV]/[^:]+:"
    return getFirstMatch(line, pattern, logErrors)
    
def removeLogPrefix_Android(lines):
    res = []
    for line in lines:
        prefix = getLogPrefix_Android(line)
        res.append(line[len(prefix):])
    return res
            
def getMultiLineLogs_Android(lines, logErrors=False):
    '''
    Example:
        [...]
        08-13 11:22:59.420: D/dalvikvm(6404): [Log details]                 <= first log
        08-13 11:22:59.420: W/ActivityManager(2216): [Log details]          <= second log
        08-13 11:22:59.420: W/ActivityManager(2216): [Log details]          <= second log
        08-13 11:22:59.420: W/ActivityManager(2216): [Log details]          <= second log
        08-13 11:22:59.460: E/dalvikvm(5917): [Log details]                 <= third log
        [...]
    :return: 2d array containing the lines grouped by log
    '''
    lineBegin = None
    matchedLines = []
    currentLog = None
    for line in lines:
        if lineBegin and currentLog and line.startswith(lineBegin):
            currentLog.append(line)
        elif line and line != "":
            if currentLog:
                matchedLines.append(currentLog)
            lineBegin = getLogPrefix_Android(line, logErrors)
            currentLog = [line]
    if currentLog:
        matchedLines.append(currentLog)
    return matchedLines
    
def parseAndroidLog(text):
    lines = textToLines(text)
    lines = removeCharacters(lines, 0, 30)
    lines = strip(lines)
    lines = removeLineWithPattern(lines, "./artifacts/generated/common/runtime/UnityEngineDebugBindings.gen.cpp")
    lines = removeLineEndingWith(lines, "Unity   :")
    lines = removeEmptyLines(lines)

    for line in lines:
        print(line)
        
def getLogContaining_Android(text, pattern):
    '''
    :param pattern: a regex pattern that will be tested against logs contained in text
    :return: A dictionary of { lineIndex : lines[] } that contains the pattern
    '''
    lines = textToLines(text)
    multiLineLogs = getMultiLineLogs_Android(lines, True)
    logDict = {}
    lineIndex = 0
    for log in multiLineLogs:
        if any(getFirstMatch(line, pattern) for line in log):
            logDict[lineIndex] = log
            #print("pattern found at line: " + str(lineIndex )+ "\n" + '\n'.join(log))
        lineIndex += len(log)
    return logDict

            
if __name__ == "__main__":
    text = common.Clipboard.get().decode("utf8")

    #To recup all files in localization
    for f in common.getFiles("C:/Users/cgailledreau/Documents/ohbibi/SUP/Unity/Assets/StreamingAssets/Data/Localization", ".obd"):
        text = common.readFile(f, fileEncoding="utf-8")
        checkAccolade(text)
        
    # parseAndroidLog("""C:\Ohbibi\Sup\Log-FreezeGuillaume.txt""")

    # text = common.Clipboard.get().decode("utf8")
    # res = countLines(lines)
    # res = [x for x in res]
    # res.sort()
    # for x in res:
    #     print("{0}".format(x[0]))


