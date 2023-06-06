#!/usr/bin/python
# takes 2 arguments: package path and extract destination path

import sys
import tarfile
import os
from os.path import *
import shutil
    
def importUnityPackage(packagePath, destinationFolder, importMetaFiles = False):
    """Import the given package to the specified path."""
    """Replace any existing files at target destination"""
    
    fileExtension = os.path.splitext(basename(packagePath))[1]
    if "unitypackage" not in fileExtension:
        raise Exception(fileExtension + " invalid file type. Except: unitypackage")
    tmpExtractPath = ".tmp_" + basename(packagePath)
    if isdir(tmpExtractPath) and exists(tmpExtractPath):
        shutil.rmtree(tmpExtractPath, ignore_errors=True)
    with tarfile.open(packagePath, "r:gz") as tar: # unitypackages are actually tar.gz files
        filesDict = { }
        tar.extractall(tmpExtractPath)
        for tarinfo in tar:
            path = tarinfo.name.split("/") # path looks like this "./GUID/assetContent" or "GUID/assetContent"
            if len(path) > 0 and path[0] == '.': # removing '.' if present
                path = path[1:]
            if len(path) == 2:
                
                # we store our asset's informations in the dictionary per GUID
                guid = str(path[0])
                if guid not in filesDict:
                    filesDict[guid] = { }
                    
                # location of the asset inside the package
                if basename(tarinfo.name) == "asset":
                    filesDict[guid]["asset"] = tarinfo.name
                    
                # location of the asset.meta inside the package
                if importMetaFiles == True and basename(tarinfo.name) == "asset.meta":
                    filesDict[guid]["meta"] = tarinfo.name
                    
                # pathname file contain the destination path of the current asset
                if basename(tarinfo.name) == "pathname":
                    # extract pathname file to read the asset path
                    if exists(normpath(join(tmpExtractPath, tarinfo.name))):
                        os.remove(normpath(join(tmpExtractPath, tarinfo.name)))
                    tar.extract(tarinfo, tmpExtractPath)
                    with open(normpath(join(tmpExtractPath, tarinfo.name)), 'r') as f:
                        filesDict[guid]["path"] = f.readline()[7:].strip() # removing 7 firsts characters "Assets/"
                        print(filesDict[guid]["path"])
                        
        for key in filesDict:
            def extractFileTo(filename, destinationPath):
                #tar.extract(filename, tmpExtractPath)
                if not os.path.exists(dirname(destinationPath)):
                    os.makedirs(dirname(destinationPath))
                if isfile(destinationPath):
                    os.remove(destinationPath)
                print(destinationPath)
                os.rename(normpath(join(tmpExtractPath, filename)), destinationPath)
            if "asset" in filesDict[key]:
                # extract the asset file and move it to its final destination
                extractFileTo(filesDict[key]["asset"], normpath(join(destinationFolder, filesDict[key]["path"])))
                if importMetaFiles == True and "meta" in filesDict[key]:
                    extractFileTo(filesDict[key]["meta"], normpath(join(destinationFolder, filesDict[key]["path"])) + ".meta")
            elif importMetaFiles == True and "meta" in filesDict[key]:
                # extract folder's meta file
                extractFileTo(filesDict[key]["meta"], normpath(join(destinationFolder, dirname(filesDict[key]["path"]))) + ".meta")

                
    if isdir(tmpExtractPath) and exists(tmpExtractPath):
        shutil.rmtree(tmpExtractPath, ignore_errors=True)
        