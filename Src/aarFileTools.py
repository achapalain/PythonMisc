#!/usr/bin/python
# taks 2 arguments: package path and extract destination path

import sys
import zipfile
import os
from os.path import *
import shutil
import datetime
import obbinstall
from Python import common


sys.dont_write_bytecode = True

def getArchiveContent(archivePath):
    """Print the list of every files presents in the archive"""
    
    with zipfile.ZipFile(archivePath, 'r') as zf:
        for info in zf.infolist():
            print(info.filename)
            
def extractFromArchive(archivePath, filename, destinationFolder, removeFromArchive = False, preserveFilePath = True):
    """Extract filename from the archive into the destinationFolder"""
    """preserveFilePath option allow you to preserve the path of your file in the destinationFolder"""
    
    print("extractFromArchive: " + archivePath + ", " + filename + ", " + destinationFolder)
    
    def extractFileFromArchive(zf, filename):
        
        buffer = zf.read(filename)
        if preserveFilePath == True:
            outFilePath = normpath(join(destinationFolder, filename))
        else:
            outFilePath = normpath(join(destinationFolder, basename(filename)))
        if not exists(dirname(outFilePath)):
            os.makedirs(dirname(outFilePath))
        with open(outFilePath, 'wb') as outFile:
            outFile.write(buffer)
            print(filename + " extracted")
    
    filesToExtract = []
    archiveWasRewriten = False
    # open the archive
    with zipfile.ZipFile(archivePath, 'r') as zf:
        # check if the file exist in the archive before re-write the archive
        fileFound = False
        for info in zf.infolist():
            if filename == "*":
                filesToExtract.append(info.filename)
            elif info.filename == filename:
                filesToExtract.append(filename)
                break
            elif info.filename.endswith(".jar") and filename.startswith(info.filename + "/"):
                # requested file is inside a .jar
                extractFromArchive(archivePath, info.filename, "_aarFileTools_tmp")
                jarFilePath = normpath(join("_aarFileTools_tmp", info.filename))
                tempDestination = jarFilePath.replace(".jar", "_export")
                extractFromArchive(jarFilePath, filename.replace(info.filename + "/", ""), tempDestination)
                if exists(tempDestination):
                    common.moveData(tempDestination, destinationFolder, copyOption=common.COPY_OPTION_MERGE_REPLACE)
                return
            elif info.filename.startswith(filename + "/"):
                # requested file is a directory
                filesToExtract.append(info.filename)
        fileFound = len(filesToExtract) != 0
        if fileFound == True:
            if removeFromArchive == False:
                for info in zf.infolist():
                    if (info.filename in filesToExtract):
                        # write the file outside our archive
                        extractFileFromArchive(zf, info.filename)
            else:
                # create a temporary archive to re-write content we dont extract
                tmpArchiveName = normpath(join(dirname(archivePath), "." + basename(archivePath) + "_tmp"))
                with zipfile.ZipFile(tmpArchiveName, 'w') as zfOut:
                    try:
                        for info in zf.infolist():
                            if (info.filename in filesToExtract):
                                # write the file outside our archive
                                extractFileFromArchive(zf, info.filename)
                            else: # write the file inside our new archive
                                buffer = zf.read(info.filename)
                                zfOut.writestr(info, buffer)
                    except:
                        os.remove(tmpArchiveName)
                        raise
                archiveWasRewriten = True
        else:
            print("File: " + filename + " not found in " + archivePath)
    if archiveWasRewriten == True:
        # replace the old archive with newly writen one
        os.remove(archivePath)
        os.rename(tmpArchiveName, archivePath)
        
def decompileJavaClasses(archivePath, destinationFolder = None):

    def decompileClassFile(filePath, replaceFile=True):
        print("decompile:" + filePath)
        os.system("javap -c " + filePath + " > " + filePath.replace(".class", ".javad"))
        if replaceFile:
            common.removeData(filePath)
            
    def foreachFileRecursive(file):
    
        if isdir(file):
            for item in os.listdir(file):
                item = normpath(join(file, item))
                if os.path.isdir(item):
                    foreachFileRecursive(item)
                elif item.endswith(".class"):
                    decompileClassFile(item)
                else:
                    print("invalid file: " + item)
    if not destinationFolder:
        destinationPath = archivePath.replace(".aar", "_decompiled/classes")
    extractFromArchive(archivePath, "classes.jar/*", destinationPath)
    
    if exists(destinationPath):
        for item in os.listdir(destinationPath):
            foreachFileRecursive(normpath(join(destinationPath, item)))
            
            
            
if __name__ == "__main__":

    if len(sys.argv) == 2:
        for item in os.listdir(sys.argv[1]):
            if item.endswith(".aar"):
                decompileJavaClasses(normpath(join(sys.argv[1], item)))
 