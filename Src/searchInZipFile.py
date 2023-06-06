#!/usr/bin/python

import sys
from os.path import *
import obbinstall
import Python.common as common
import zipfile

def searchInZipFile(file, searchTerm):
    archive = zipfile.ZipFile(file, 'r')
    destinationDir = dirname(file) + "/." + basename(file) + "_dir"
    archive.extractall(destinationDir)
    
    files = common.getFiles(destinationDir)
    striplen = len(destinationDir) + 1
    ret = []
    for f in files:
        if searchTerm in f[striplen:]:
            ret.append(basename(file) + ": " + f[striplen:])
        
    common.removeData(destinationDir)
    return ret
    
def findInFolder(folder, searchTerm):
    files = common.getFiles(folder)
    ret = []
    for f in files:
        fileExtension = splitext(f)[1]
        if fileExtension == ".aar" or fileExtension == ".jar" or fileExtension == ".zip":
            fileFound = searchInZipFile(f, searchTerm)
            for found in fileFound:
                ret.append(found)
    return ret

if len(sys.argv) > 0 and sys.argv[0] == __file__:
    print(findInFolder("D:/Ohbibi/Git/Kart/Unity/Assets/Plugins/Android", "libgpg"))