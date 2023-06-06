#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, json, obbinstall
from os.path import *
from Python import jsonUtils, common
from collections import OrderedDict

def toStr(obj):
    return str(obj).encode('utf-8')

def getBindingFilesFromFidelioConf(unityPath, storageClass):
    unityProjectPath = normpath(unityPath)
    streamingAssetsDir = normpath(join(unityProjectPath, "Assets", "StreamingAssets"))
    unityConf = jsonUtils.load(join(streamingAssetsDir, "fidelioUnity.conf"))
    if unityConf and "ObdBindings" in unityConf:
        for binding in unityConf["ObdBindings"]:
            if storageClass in binding["StorageClass"]:
                return [normpath(f) for f in binding["Files"]]
    return None

def splitLocalizationFile(filePath):
    
    jsonObject = jsonUtils.load(filePath)
    rootDir = dirname(filePath)
    fileName = basename(filePath)
    langStrings = {}
    splitFilesOutput = []
    
    for k in jsonObject:
    
        ID = k["ID"]
        
        for k, v in k.items():
            if k != "ID":
                langName = k[:2] # get first to char of string
                if langName == k:
                    if langName not in langStrings:
                        # an array of {ID: "", Values: ""} because:
                        # array are required by fidelio to convert protobuf..
                        # "ID" field is required for the class needs to inherit from OhBiData.GameData
                        orderedDictForLanguage = OrderedDict()
                        orderedDict = OrderedDict()
                        orderedDictForLanguage["ID"] = langName
                        orderedDictForLanguage["Values"] = orderedDict
                        langStrings[langName] = [orderedDictForLanguage]
                    langStrings[langName][0]["Values"][ID] = v
                
    for lang in langStrings:
        langDirectory = normpath(join(rootDir, lang))
        langFile = normpath(join(langDirectory, fileName))
        common.ensureDirectoryExists(langDirectory)
        with open(langFile, 'wb') as outfile:
            content = json.dumps(langStrings[lang], ensure_ascii=False, indent=2).encode('utf-8')
            outfile.write(content)
            splitFilesOutput.append(langFile)
    return splitFilesOutput
        
################################################################################
if __name__ == "__main__":
    
    print(splitLocalizationFile(sys.argv[1]))
