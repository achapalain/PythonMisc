#!/usr/bin/env python
# -*- coding: latin-1 -*-

import os, sys, collections, copy
from os.path import *
import obbinstall


from starLordConfig import *

starLord = StarLordConfig()

filteredDirs = [
    "_OLD",
    #"Editor",
    "Resources/sound",
    "StreamingAssets/skins",
]

suspects = [
    "~HEAD",
]

allowedExtensions = [
    ".meta",
    ".prefab",
    ".asset",
    ".fbx",
    ".obj",
    ".controller",
    ".json",
    ".mat",
    ".shader",
    ".cubemap",
    ".png",
    ".tga",
    ".jpg",
    ".jpeg",
    ".anim",
    ".txt",
    ".skel",
    ".otf",
    ".js",
    ".cs",
]

def getMatch(s, listValues):
    for v in listValues:
        if v in s:
            return v

def printMsg(s):
    print("\t" + s)

def checkResources():
    print("Checking Resources directory ...")
    
    filteredDirsLower = copy.copy(filteredDirs)
    for i in range(0, len(filteredDirsLower)):
        filteredDirsLower[i] = normpath(filteredDirsLower[i].lower())
        
    for dirpath, dirnames, filenames in os.walk(join(starLord.assetsDir, "Resources")):
        dirpathLower = dirpath.lower()
        isFiltered = False
        for v in filteredDirsLower:
            if v in dirpathLower:
                isFiltered = True
                break
        if isFiltered:
            continue
        for f in filenames:
            lowerf = f.lower()
            (root, ext) = splitext(lowerf)
            if ext.lower() not in allowedExtensions or getMatch(f, suspects):
                fullpath = join(dirpath, f)
                printMsg("Found unexpected file: " + fullpath)
                    
checkResources()
print("Done")
