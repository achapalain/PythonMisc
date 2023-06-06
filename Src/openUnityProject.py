#!/usr/bin/python

import sys, subprocess, re, os
from os.path import *
import obbinstall
from Python import common, unity, gameSettings

DETACHED_PROCESS = 0x00000008

if len(sys.argv) > 0 and sys.argv[0] == __file__:
    gs = gameSettings.GameSettings()
    
    cacheUnityFolderFile = join(dirname(__file__), "UnityInstallCache.txt")
    cacheUnityFolderArray = [""]
    if exists(cacheUnityFolderFile):
        cacheUnityFolderArray = common.readFile(cacheUnityFolderFile).split('\n')
        
    unityProjectFolder = normpath(join(dirname(abspath(sys.argv[0])), "../../../Unity"))
    unityVersion = None
    
    # search for the last version used to open this project
    unityVersion = unity.getCurrentUnityVersionOfProject(unityProjectFolder)
    if not unityVersion:
        unityVersion = gs.Project.unityVersion
        
    unityInstallFolder = unity.getUnityInstallRootDir(unityVersion, cacheUnityFolderArray)
    
    if not unityInstallFolder and common.isWindowsOS():
        
        # ask the user to pick his unity install folder
        execFileFound = common.browseForFile("/", [("exec files", "*.exe")])
        if execFileFound:
            cacheUnityFolderArray.append(dirname(dirname(dirname(execFileFound)))) # save the directory in which unity is installed
            common.writeFile(cacheUnityFolderFile, "\n".join(cacheUnityFolderArray))
            unityInstallFolder = dirname(dirname(execFileFound))
        else:
            sys.exit() # quit
            
    if common.isWindowsOS():
        unityInstallFolder = normpath(join(unityInstallFolder, "Editor/Unity.exe"))
    else:
        unityInstallFolder = normpath(join(unityInstallFolder, "Unity.app/Contents/MacOS/Unity"))

    print(unityInstallFolder)
    
    command = [unityInstallFolder, "-projectPath", unityProjectFolder]
    
    subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, creationflags=DETACHED_PROCESS)
