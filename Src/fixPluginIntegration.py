#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, collections, obbinstall
from os.path import *
import Python.common as common

precompileBegin = "#if UNITY_ANDROID"
precompileEnd = "#endif"

assetsDir = "../../../Unity/Assets"

def fixGPGS():
    # Removing iOS compilation
    files = common.getFiles(join(assetsDir, "GooglePlayGames"), ".cs")
    for f in files:
        if not f.endswith(".cs"):
            continue
        changed = False
        with open(f) as file:
            text = file.read()
            if "\r\n" in text:  eol = "\r\n"
            else:               eol = "\n"
            if not text.startswith(precompileBegin):
                while text.startswith(eol):
                    text = text.replace(eol, "", 1)
                while text.endswith(eol):
                    p1, p2, p3 = text.rpartition(eol)
                    text = p1
                text = precompileBegin + eol + eol + text + eol + eol + precompileEnd + eol
                changed = True
        if changed:
            print("Updating: ", f)
            with open(f, "w") as f:
                f.write(text)

    # Removing unused files on iOS
    removedFiles = [
        join(assetsDir, "GooglePlayGames/Editor/GPGSPostBuild.cs"),
        join(assetsDir, "Plugins/iOS/GPGSAppController.h"),
        join(assetsDir, "Plugins/iOS/GPGSAppController.mm"),
    ]
    for f in removedFiles:
        print("Removing:", f)
        common.removeData(f)

def fixHyprMX():
    targetFile = "HyprMXSettings.cs"
    files = common.getFiles(join(assetsDir, "HyprMXSettings"), ".cs")
    if len(files) == 0:
        print("Could not find " + targetFile)
        return

    with open(files[0]) as f:
        text = f.read()
        if "\r\n" in text:  eol = "\r\n"
        else:               eol = "\n"

        searched = '			project.AddFrameworkToProject (targetId, "UIKit.framework", false);'
        addition = '			project.AddFrameworkToProject (targetId, "libxml2.tbd", false);'
        if (addition not in text):
            text = text.replace(searched, searched + eol + addition)

        with open(f, "w") as f:
            f.write(text)

if __name__ == "__main__":
    fixGPGS()
    # fixHyprMX()

    print("Done")
