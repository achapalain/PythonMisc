#!/usr/bin/env python
# -*- coding: utf-8 -*-

import obbinstall
import sys, json, collections, re, csv
import Framework.common as common

errors = []
warnings = []
silent = False

def getErrors():
    return errors

def getWarnings():
    return warnings

def printMsg(*args):
    if not silent:
        print(args)

def printError(text):
    if not silent:
        res = '### ERROR ' + text
        errors.append(res)
        print(res)

def printWarning(text):
    if not silent:
        res = '### WARNING ' + text
        warnings.append(res)
        print(res)

################################################################################
## LoadJson
# TODO: handle UTF-8 with BOM file format:
# json.load(codecs.open(path, "r", "utf-8-sig"))
def load(path, fileEncoding=None, unknownEncoding=False):
    # try:
    jsonData = None
    if not fileEncoding:
        try:
            jsonData = common.readFile(path, throwExceptions=True)
        except UnicodeDecodeError as e:
            try:
                # file has special encoding
                jsonData = common.readFile(path, 'utf-8')
            except UnicodeDecodeError as e:
                raise Exception("Failed to read file with encodings=Unicode, utf-8. Please specify the correct encoding.")
    else:
        jsonData = common.readFile(path, fileEncoding)
    try:
        data = json.JSONDecoder(object_pairs_hook = collections.OrderedDict).decode(jsonData)
        return data
    except BaseException as e:
        print(e, "\n", "Invalid JSON file:", path)

def loadFromText(text):
    return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(text)

def readFile(path, fileEncoding=""):
    return removeComments(common.readFile(path, fileEncoding))
        
#===============================================================================
def _json_object_hook(d):
    return collections.namedtuple('X', d.keys())(*d.values())
def rawJsonToObj(rawData):
    return json.loads(rawData, object_hook=_json_object_hook)
def jsonFileToObj(filePath):
    with open(filePath, 'r') as f:
        content = f.read()
        return rawJsonToObj(content)
        
################################################################################
## SaveToFile
def save(data, jsonFile, encoding=None, indent=2, separators=None, newline="\n"):
##    if encoding == None:
##        import locale
##        encoding = locale.getpreferredencoding(False)
    (dirPath, _, _) = common.getFileParts(jsonFile)
    if dirPath and dirPath != "":
        common.ensureDirectoryExists(dirPath)
    outFile = None
    if encoding != None:
        # printMsg('*** Saving: ' + jsonFile + " (" + encoding.upper() + ")")
        outFile = open(jsonFile, 'w', encoding=encoding, newline=newline)
    else:
        # printMsg('*** Saving: ' + jsonFile + " (" + "No Encoding" + ")")
        outFile = open(jsonFile, 'w', newline=newline)
    json.dump(data, outFile, indent=indent, ensure_ascii=False, separators=separators)

def jsonToCSV(jsonFiles, outputFile):
    jsonDictionaries = []
    keys = []
    for file in jsonFiles:
        jsonRaw = common.readFile(file)
        j = json.loads(jsonRaw)
        jsonDictionaries.append(j)
        for k in j:
            if k not in keys:
                keys.append(k)
                
                
    print("All keys: " + str(keys))

    csvWriter = csv.writer(open(outputFile, "w", newline=''))
    csvWriter.writerow(keys)

    for j in jsonDictionaries:
        newRow = []
        for k in keys:
            if k in j:
                newRow.append(j[k])
            else:
                newRow.append("")
        csvWriter.writerow(newRow)
    
def removeComments(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def diff(data1, data2, path=[]):
    removed = []
    added = []
    changed = []

    def diffContent(x1, x2, path):
        if type(data1) != type(data2):
            changed.append(".".join(path))
            return
        if isinstance(x1, list):
            minSize = min(len(x1), len(x2))
            for i in range(minSize):
                if x1[i] != x2[i]:
                    diffContent(x1[i], x2[i], path + ["[" + str(i) + "]"])
            if len(x1) > minSize:
                for i in range(minSize, len(x1)):
                    removed.append(path + ["[" + str(i) + "]"])
            elif len(x2) > minSize:
                for i in range(minSize, len(x2)):
                    added.append(path + ["[" + str(i) + "]"])
        elif isinstance(x1, dict):
            for key in set(list(x1.keys()) + list(x2.keys())):
                if key not in x1:
                    added.append(path + [key])
                elif key not in x2:
                    removed.append(path + [key])
                else:
                    x1Child = x1[key]
                    x2Child = x2[key]
                    if x1Child != x2Child:
                        diffContent.append(x1Child, x2Child, path + [key])
        elif x1 != x2:
            changed.append(path)

    diffContent(data1, data2, path)

    return removed, added, changed
