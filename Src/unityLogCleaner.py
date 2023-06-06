from Framework import stringOperations as so


# def processOld(logPath)
#     rawText = common.readFile(logPath)
#     lines = rawText.split('\n')
#     newlines = []
#
#     def getSpecialLine(line):
#         if line.startswith("-----Compiler Commandline Arguments:"):
#             return "BeginCompilation"
#         elif line.startswith("-----CompilerOutput:-stderr"):
#             return "EndCompilation"
#         return ""
#
#     lineCount = len(lines)
#     i = 0
#     while i < lineCount:
#         line = lines[i]
#         if getSpecialLine(line) == "BeginCompilation":
#             while getSpecialLine(line) != "EndCompilation" and i < lineCount:
#                 line = lines[i]
#                 i += 1
#         newlines.append(line)
#         i += 1
#     fileAndExt = splitext(sys.argv[1])
#     common.writeFile(fileAndExt[0] + "cleaned" + fileAndExt[1], '\n'.join(newlines))
#
# if len(sys.argv) > 1:
#     processOld(sys.argv[1])

def process(filePathIn, filePathOut):
    lines = so.textToLines(filePathIn)
    lines = so.removeEmptyLines(lines)

    def replaceParam(lines, startingPattern, replacement):
        for line in lines:
            if startingPattern in line:
                searched = line[line.index(startingPattern) + len(startingPattern):]
                return so.replace(lines, searched, replacement)
        return lines

    lines = replaceParam(lines, "-buildNumber ", "BUILD_NUMBER")
    lines = replaceParam(lines, "-buildVersion ", "BUILD_VERSION")

    lines = so.removeLineWithPattern(lines, "[Fps-Android] $ /bin/sh -xe /var")
    lines = so.removeLineWithPattern(lines, "; Context handle")
    lines = so.removeLineWithPattern(lines, "Responsefile: Temp/UnityTempFile-")
    lines = so.removeLineWithPattern(lines, "Refresh: trashing asset")
    lines = so.removeLineWithPattern(lines, "Launching external process:")
    lines = so.removeLineWithPattern(lines, "Warming cache for")
    lines = so.removeLineWithPattern(lines, "Unused Serialized files")
    lines = so.removeLineWithPattern(lines, "unused Assets to reduce memory usage")
    lines = so.removeLineWithPattern(lines, "Updating .* - GUID")
    lines = so.removeLineWithPattern(lines, "Generated new Fabric build ID")
    lines = so.removeLineWithPattern(lines, "format is not supported, decompressing texture")
    lines = so.removeLineWithPattern(lines, "Updating Assets/MessagePackGenerated - ")
    lines = so.removeLineWithPattern(lines, "Thread -> id: ")
    # lines = so.removeLineWithPattern(lines, "Checking out files")
    # lines = so.removeLineWithPattern(lines, " create mode ")
    # lines = so.removeLineWithPattern(lines, " delete mode ")
    # lines = so.removeLineWithPattern(lines, " rename ")
    # lines = so.removeLineStartingWith(lines, "Removing ")
    # lines = so.removeLineWithPattern(lines, "mono_pe_file_map")
    # lines = so.removeLineWithPattern(lines, "format is not supported, decompressing texture")

    lines = so.removeLinesBlock(lines, "Updating git", "Git SHA1 summary")
    lines = so.removeLinesBlock(lines, "Running as SYSTEM", "Jenkins parameters")
    # lines = so.removeLineStartingWith(lines, "'Assets/")
    # lines = so.removeLinesBlock(lines, "-----Compiler Commandline Arguments", "-----CompilerOutput")
    # lines = so.removeLinesBlock(lines, "Updating Assets/", " done. [Time")
    # lines = so.removeLinesBlock(lines, "Started by timer", "Git SHA1 summary")
    # lines = so.removeLinesBlock(lines, "Fast-forward", "insertions(+)")
    lines = so.removeLinesBlock(lines, "Google.Logger:Log", "UnityEditor.EditorAssemblies:ProcessInitializeOnLoadAttributes")
    lines = so.removeLinesBlock(lines, "Fabric.Internal.Editor.Utils:Warn", "AutoBuilder:PerformAndroidBuild")
    lines = so.removeLinesBlock(lines, "Fabric.Internal.Editor.Utils:Log", "AutoBuilder:PerformAndroidBuild")
    # lines = so.removeLinesBlock(lines, "InjectBundleAndSDKVersion", "AutoBuilder:PerformAndroidBuild")
    # lines = so.removeLinesBlock(lines, "While loading :", "Dependency found at")
    # lines = so.removeLinesBlock(lines, "GameDataConverter Initialized with dataManagers", " : Done")
    # lines = so.removeLinesBlock(lines, "Removing Splited Localization files", "Checking fidelioUnity.conf")
    lines = so.removeLinesBlock(lines, "Compiled shader", "gles3 (")
    # lines = so.removeLinesBlock(lines, "file(s) to restore", "Widgets.protobw")

    lines = so.reorderMatchingPattern(lines, "-r:'")


    lines = so.replace(lines, "/Users/jenkins", "")
    lines = so.replace(lines, "/Users/developerohbibi", "")
    lines = so.replace(lines, "\@Temp\/UnityTempFile\-[a-f0-9]+", "@Temp/UnityTempFile-XXXXXXXXXXXXXXXX", useRegex=True)
    lines = so.replace(lines, "timestamp \d+", "timestamp XXXXXXXXXXXXXXXX", useRegex=True)
    lines = so.replace(lines, "0x[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]+", "0xXXXXXXXXX", useRegex=True)
    lines = so.replace(lines, "\d+\.\d+\.\d+\.\d+\:\d+", "XX.XX.XX.XX:XXXXX", useRegex=True)
    lines = so.replace(lines, "\d\d\d\d\d\d \d+\:\d+:\d+", "XXXXXX XX:XX.XX", useRegex=True)
    lines = so.replace(lines, "\d\d\:\d\d\:\d\d\.\d+", "XX:XX:XX:XX.XXX", useRegex=True)
    lines = so.replace(lines, " PM ", " ", useRegex=True)
    lines = so.replace(lines, " AM ", " ", useRegex=True)
    lines = so.replace(lines, "\d+\:\d+\:\d+", "XX:XX:XX", useRegex=True)
    lines = so.replace(lines, "\d+\-\d+\-\d+", "XX-XX-XX", useRegex=True)
    lines = so.replace(lines, "\d+\/\d+\/\d+", "XX/XX/XX", useRegex=True)
    lines = so.replace(lines, "\d\d\:\d\d\:\d\d\.\d+", "XX:XX:XX:XX.XXX", useRegex=True)
    lines = so.replace(lines, "Port \d+ was selected", "Port XXXXX was selected", useRegex=True)
    lines = so.replace(lines, "\d+ bytes", "XXX bytes", useRegex=True)
    lines = so.replace(lines, "\d+ milliseconds", "XXX milliseconds", useRegex=True)
    lines = so.replace(lines, "\d+.\d+ ms", "X.XX ms", useRegex=True)
    lines = so.replace(lines, "\d+.\d+ s", "X.XX s", useRegex=True)
    lines = so.replace(lines, "\d+.\d+s.", "X.XXs.", useRegex=True)
    lines = so.replace(lines, "\d+.\d+ GB", "X.XX GB", useRegex=True)
    lines = so.replace(lines, "\d+.\d+ MB", "XX.XX MB", useRegex=True)
    lines = so.replace(lines, "\d+.\d+ mb", "XX.XX mb", useRegex=True)
    lines = so.replace(lines, "Loaded Objects now: \d+", "Loaded Objects now: XXX", useRegex=True)
    lines = so.replace(lines, "Updating Assets/StreamingAssets/.*", "Updating Assets/StreamingAssets/Data/XXXXXXXX", useRegex=True)
    lines = so.replace(lines, "----- Compute hash for Assets/StreamingAssets/.*", "----- Compute hash for Assets/StreamingAssets/XXXXXXXX", useRegex=True)

    # TMP
    lines = so.removeLinesBlock(lines, "### Cleaning protobuf sources ...", "### Unity build", keepEnd=True)

    so.printIntoFile(filePathOut, lines)

process(r"C:\Perso\Compare1.txt", r"C:\Perso\Compare1_.txt")
process(r"C:\Perso\Compare2.txt", r"C:\Perso\Compare2_.txt")