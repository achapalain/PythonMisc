#!/usr/bin/python

import obbinstall, sys, tarfile, os
from os.path import *
from Python import common, unity

def findDuplicateMetas():
    """
    When doing framework merge many files exists both in the project and in the framework
    """
    path = join(unity.getNearestProjectPath(), "Assets")
    allMetas = common.getFiles(path, ".meta")
    fileNamesDict = {}
    for x in allMetas:
        if ".cs" not in x: continue
        fileName = basename(x)
        if fileName not in fileNamesDict:
            fileNamesDict[fileName] = [x]
        else:
            fileNamesDict[fileName].append(x)
    duplicates = {}
    for x in fileNamesDict:
        if len(fileNamesDict[x]) >= 2:
            duplicates[x] = fileNamesDict[x]
            print(x)
            for y in fileNamesDict[x]:
                print("\t" + y)

# findDuplicateMetas()

inputDict = {
    "Unity/Assets/Editor/Utils/ColorsToCS.cs.meta"								 : "f7bc89e3c46f5c540a34bfef298c784c",
    "Unity/Assets/Editor/Utils/PlayerPrefsEditor/PlayerPrefStore.cs.meta"        : "bef7cc91beb5b4b6382673e26800778a",
    "Unity/Assets/Editor/Utils/PlayerPrefsEditor/PlayerPrefsEditor.cs.meta"      : "4b68ebe8085db460cbd3707041ea894f",
    "Unity/Assets/Editor/Utils/ReorderableArrays.cs.meta"                        : "fac5e55f78449554da589a8a35914572",
    "Unity/Assets/Editor/Utils/SaveMesh.cs.meta"                                 : "da404d375b4c38540bbbb4ea7c2f951f",
    "Unity/Assets/Editor/Utils/SceneExplorer.cs.meta"                            : "1c86a4a3b9a70dc43a3e5c261aa6171f",
    "Unity/Assets/Editor/Utils/ScreenshotTaker.cs.meta"                          : "1f43438d3f4cd402f8f372cbb8930f66",
    "Unity/Assets/Editor/Utils/ShowFileExtensions.cs.meta"                       : "7a26a5efeeb2379498386078728c7319",
    "Unity/Assets/Editor/Utils/WorldInfos.cs.meta"                               : "54761bb157e713740bb55267c5a4514c",
    "Unity/Assets/Scripts/Debug/DebugLabel.cs.meta"                              : "77f826a420655324d9cfbf78cbec09b1",
    "Unity/Assets/Scripts/Debug/FPSDisplay.cs.meta"                              : "c5b6c53de31c64a458f0fa182ff3f1d0",
    "Unity/Assets/Scripts/Debug/GridOrganizer.cs.meta"                           : "675eb487b869ead4e844d843f3994a38",
    "Unity/Assets/Scripts/Debug/SupFPSCounter.cs.meta"                           : "a385dafba12f79c4b9d228f650c78a2a",
    "Unity/Assets/Scripts/Graphics/Downscaler.cs.meta"                           : "ab712ee7df7b6e446826299fd2b318cc",
    "Unity/Assets/Scripts/Touch/ButtonHandler.cs.meta"                           : "85bf3be603548374ca46f521a3aa7fda",
    "Unity/Assets/Scripts/Touch/TouchCreator.cs.meta"                            : "74dc52e147618524888ebd52009e630a",
    "Unity/Assets/Scripts/Touch/TouchHandler.cs.meta"                            : "e7fb9ae8f1430b044a0af185412128d6",
    "Unity/Assets/Scripts/Touch/TouchInstance.cs.meta"                           : "9d88c9a8168148d41b5f1e0f8cdb127d",
    "Unity/Assets/Scripts/Touch/VirtualTouchPad.cs.meta"                         : "76af4750ff012f549b025324f33f548e",
    "Unity/Assets/Scripts/Utils/DebugExtension.cs.meta"                          : "c85339db2e28cd84aafa70d1ef63e6cc",
    "Unity/Assets/Scripts/Utils/ObjectFollower.cs.meta"                          : "170a96b49b5f72c4089819e19937d3e3",
    "Unity/Assets/Scripts/Utils/StringFast.cs.meta"                              : "57098fc63647f34488ff30b56cd55f9f",
    "Unity/Assets/Scripts/Debug/EditorLabel.cs.meta"                             : "0ad21411ae826c34f9cd9257f68d697d",
    "Unity/Assets/Scripts/Utils/EventArray.cs.meta"                              : "95224ff022534f84cbef55c07c77fdba",
    "Unity/Assets/Scripts/Utils/FPSCounter.cs.meta"                              : "c78e99e9b6b2645879f5bd38dd5a7ec1",
    "Unity/Assets/Scripts/Utils/ScreenResizeDetector.cs.meta"                    : "3a4f388d3d7cb43c89b5ca87bf513644",
    "Unity/Assets/Scripts/Utils/SetSceneToActive.cs.meta"                        : "9de98c3020007554dabaeaf4e80c41a2",
}

inputFiles = [
    "Scenes/00_Main",
    "Scenes/Level",
    "Characters/Angelo/Angelo",
    "Characters/Angelo/Cutscene/Angelo",
    "Characters/BigDaddy/BigDaddy",
    "Characters/Cobra/Cutscene/Cobra",
    "Characters/Cobra/Cutscene/Cobra2",
    "Characters/CrocMcFly/CrocMcFly",
    "Characters/CrocMcFly/Cutscene/CrocMcFly",
    "Characters/Demona/Demona",
    "Characters/DragonFist/Custcene/DragonFist",
    "Characters/DragonFist/DragonFist",
    "Characters/ElsaDorsa/ElsaDorsa",
    "Characters/Ghostmonaute/Cutscene/Ghostmonaute",
    "Characters/Ghostmonaute/Ghostmonaute",
    "Characters/KenDrift/KenDrift",
    "Characters/Khaled/Cutscene/Khaled",
    "Characters/Khaled/Fix/Khaled",
    "Characters/Khaled/Khaled_Leopard",
    "Characters/Kissmortan/Kissmortan",
    "Characters/MagicAce/MagicAce",
    "Characters/McIronbot/Cutscene/McIronbot",
    "Characters/McIronbot/Cutscene/McIronbot_02",
    "Characters/McIronbot/McIronbot",
    "Characters/McIronbot/McIronbot_02",
    "Characters/Miyuki/Miyuki",
    "Characters/Monarch/Cutscene/Monarch",
    "Characters/Monarch/Monarch",
    "Characters/Overtaker/Animations/Confetis",
    "Characters/Overtaker/Overtaker",
    "Characters/PeterPhoenix/PeterPhoenix",
    "Characters/PinUp/Cutscene/PinUp",
    "Characters/PinUp/Cutscene/PinUp_02",
    "Characters/PinUp/PinUp",
    "Characters/Punk/Punk",
    "Characters/Punk/Punk_Hyene",
    "Characters/Sergei/Sergei",
    "Characters/Sergei/Sergei3",
    "Characters/Stalione/Stalione",
    "Characters/Sunset/Sunset",
    "Characters/TankGirl/Cutscene/TankGirlCut",
    "Characters/TankGirl/TankGirl",
    "Characters/TankGirl/TankGirlCut",
    "Characters/Valentino/Valentino",
    "Prefabs/_old/oldPlayer",
    "Prefabs/Dummy",
    "Prefabs/Managers/01_GameplayManager",
    "Prefabs/Managers/05_GraphicsManager",
    "Prefabs/Resources/Player",
    "Prefabs/Turret",
    "Prefabs/UI/VictoryAnimation",
    "Prefabs/Weapons/HealerGun",
    "Prefabs/Weapons/Rifle",
    "Prefabs/Weapons/Shotgun",
    "Prefabs/Weapons/Sniper"
]

inputDict = {basename(x).replace(".meta", ""): inputDict[x] for x in inputDict}

def findUpdatedMetas(oldMetaDict):
    """
    :param oldMetaDict: Dictionary of (file, meta)
    :return: Dictionary of oldGuid:(file, newGuid)
    """
    path = join(unity.getNearestProjectPath(), "Assets")
    allCs = common.getFiles(path, ".cs")
    fileNames = {basename(x): x for x in allCs}
    guidText = "guid: "
    newMetaDict = {}
    for fileName in oldMetaDict:
        if fileName not in fileNames:
            print("Couldn't find new version of:", fileName)
            continue
        # Parse new meta for GUID
        text = common.readFile(fileNames[fileName] + ".meta").replace("\r", "")
        begin = text.find(guidText) + len(guidText)
        guid = text[begin:text.find("\n", begin)]
        if guid != oldMetaDict[fileName]:
            newMetaDict[oldMetaDict[fileName]] = (fileName, guid)
            print("Need to update", fileName, oldMetaDict[fileName], "=>", guid)
    return newMetaDict

def processReplacements(files, guidReplacements):
    path = join(unity.getNearestProjectPath(), "Assets")
    allUnityFiles = [x.replace("\\", "/") for x in common.getFiles(path, onlyFiles=True)]
    for f in files:
        f = f.replace("\\", "/")
        for target in allUnityFiles:
            if f not in target:
                continue
            text = common.readFile(target)
            if not text:
                print("Could not load", target)
                continue
            updated = []
            for oldGuid in guidReplacements:
                if oldGuid in text:
                    text = text.replace(oldGuid, guidReplacements[oldGuid][1])
                    updated.append(guidReplacements[oldGuid][0])
            if len(updated) > 0:
                print("Updated", target)
                for x in updated:
                    print("\t", x)
                common.writeFile(target, text)

replacements = findUpdatedMetas(inputDict)
if len(replacements) > 0:
    print("=================================================================")
    processReplacements(inputFiles, replacements)



