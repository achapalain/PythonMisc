import obbinstall
from os.path import *
from Python import common
from Git import git
import sys, json, collections, random, re

ENABLE_FULL_LOG = False

def GenerateGUID():
    def genPart():
        def RandomChar():
            return random.choice("ABCDEF123456789")
        return RandomChar() + RandomChar() + RandomChar() + RandomChar()
    ret = "{" + genPart() + genPart() + "-" + genPart() + "-" + genPart() + "-" + genPart() + "-" + genPart() + genPart() + genPart() + "}"
    return ret
    
projectRoot = git.getFarhestGitRoot(dirname(__file__))
print(projectRoot)
    
netTarget = common.askChoice("Select a .NET target", collections.OrderedDict([
                        ("3.5", ".NET 3.5"),
                        ("4.0", ".NET 4.0")
                        ]))


# Parse solution for existing infos
solutionPath = normpath(join(projectRoot, "Dev/Game-Assembly-CSharp.sln"))
print("Loading Game solution")
solutionLines = common.readFile(solutionPath).split('\n')
projectDict = collections.OrderedDict({})

solutionFolders = ["Core", "Editor", "Game"]
globalSectionDict = collections.OrderedDict({})
projectPrefix = ""
projectPrefixFolder = ""
headerLines = []
currentGlobalSection = None

for l in solutionLines:
    if l.startswith("Project("):
        # read project info
        projectPrefix = l[:l.index(") = ") + 4] #grab the first part 'Project("{...}") = '
        infoArray = l[len(projectPrefix):].split(", ") # split the rest
        # Example: "NGUI", "..\Unity\NGUI.csproj", "{BB8D9B3B-4D5A-EE6B-744C-B5C5852B4393}"
        projectName = infoArray[0][1: -1]
        projectRelativePath = infoArray[1][1: -1]
        projectGUID = infoArray[2][1: -1]
        
        projectInfo = {}
        projectInfo["projectName"] = projectName
        projectInfo["projectGUID"] = projectGUID
        projectInfo["projectRelativePath"] = projectRelativePath
        projectInfo["projectFullPath"] = normpath(join(dirname(solutionPath), projectRelativePath))
        if not projectRelativePath.endswith("csproj"):
            projectInfo["isFolder"] = True
            projectInfo["projectTypeGUID"] = "{2150E333-8FDC-42A3-9474-1A3956D46DE8}"
        else:
            projectInfo["isFolder"] = False
            projectInfo["projectTypeGUID"] = "{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}"
        projectInfo["ManagedByUnity"] = "..\\Unity" in projectRelativePath
        
        if not projectInfo["isFolder"]:
            if exists(projectInfo["projectFullPath"]):
                projectDict[projectName] = projectInfo
            else:
                print("Project " + projectInfo["projectFullPath"] + " is referenced in the solution but is not present on disk. Removing it.")
        elif projectInfo["projectName"] in solutionFolders:
            projectDict[projectName] = projectInfo
        
        if ENABLE_FULL_LOG:
            print((" > " if projectType == FOLDER_TYPE else "") + projectName)
            print("\t " + projectRelativePath)
            print("\t " + projectGUID)
            
    elif not projectPrefix: # grab lines until first project is defined
        headerLines.append(l)
    
    if "\tGlobalSection" in l:
        currentGlobalSection = {}
        sectionName = l
        m = re.search("\((.*)\)", l)
        if m:
            sectionName = m.groups()[0]
        currentGlobalSection["Name"] = sectionName
        currentGlobalSection["Lines"] = []
        globalSectionDict[sectionName] = currentGlobalSection
        
    if currentGlobalSection:
        currentGlobalSection["Lines"].append(l)
        if "EndGlobalSection" in l:
            currentGlobalSection = None
    
# Scan csproj in unity project
unityProject = normpath(join(projectRoot, "Unity"))

print("Scanning " + unityProject + " for csproj files")
unityCSProjList = common.getFiles(unityProject, recursive=False, onlyFiles=True, restrictedExtension=".csproj")
print("Found " + str(len(unityCSProjList)) + " files")
for f in unityCSProjList:
    f = normpath(f)
    m = re.search("<ProjectGuid>({.*})", common.readFile(f))
    if m:
        projectGUID = m.groups()[0]
    else:
        print("ERROR: Could not find project guid in csproj (" + j + ")")
        projectGUID = GenerateGUID() 
    projectName = splitext(basename(f))[0]
    if projectName not in projectDict: #add the project to the solution if not already present
        print(projectName + " found in Unity folder. Adding to solution")
        projectInfo = {}
        projectInfo["projectName"] = projectName
        projectInfo["projectFullPath"] = f
        projectInfo["projectRelativePath"] = relpath(f, dirname(solutionPath))
        projectInfo["projectGUID"] = projectGUID
        projectInfo["ManagedByUnity"] = True
        projectInfo["projectTypeGUID"] = "{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}"
        projectInfo["isFolder"] = False
        # print(json.dumps(projectInfo, indent="\t"))
        # continue
        projectDict[projectName] = projectInfo
        
        
        
# ensure the following sections exists
mandatorySections = ["SolutionConfigurationPlatforms", "ProjectConfigurationPlatforms"]
for m in mandatorySections:
    if m not in globalSectionDict:
        print("ERROR: missing " + m + " section")
        sys.exit(1)
        
if "NestedProjects" in globalSectionDict:
    # Check solution folders
    for solutionFolder in solutionFolders:
        def CreateProjectFolder(name):
            projectInfo = {}
            projectInfo["projectName"] = name
            projectInfo["projectFullPath"] = name
            projectInfo["projectRelativePath"] = name
            projectInfo["projectGUID"] = GenerateGUID()
            projectInfo["ManagedByUnity"] = False
            projectInfo["isFolder"] = True
            projectInfo["projectTypeGUID"] = "{2150E333-8FDC-42A3-9474-1A3956D46DE8}"
            return projectInfo
        if solutionFolder not in projectDict:
            projectDict[solutionFolder] = CreateProjectFolder(solutionFolder)

    # Asign solution folders to each project in the solution
    # 'Game' or 'Editor' folder for every project managed by unity
    # 'Core' folder for every other projets (OhbibiCore, FidelioFramework-Core, GameScripts)
    for project in projectDict.values():
        if not project["isFolder"]:
            if project["ManagedByUnity"]:
                if project["projectName"].endswith("Editor"):
                    project["parentFolderGUID"] = projectDict["Editor"]["projectGUID"]
                else:
                    project["parentFolderGUID"] = projectDict["Game"]["projectGUID"]
            else:
                project["parentFolderGUID"] = projectDict["Core"]["projectGUID"]


        
        
        
def GetProjectConfigurationLines(projectInfo):
    lines = []
    if projectInfo["ManagedByUnity"]:
        lines.append("\t\t" + projectInfo["projectGUID"] + ".Debug|Any CPU.ActiveCfg = Debug|Any CPU")
        lines.append("\t\t" + projectInfo["projectGUID"] + ".Release|Any CPU.ActiveCfg = Release|Any CPU")
    else: # enable build only for non Unity Managed projects
        lines.append("\t\t" + projectInfo["projectGUID"] + ".Debug|Any CPU.ActiveCfg = Debug-"+netTarget+"|Any CPU")
        lines.append("\t\t" + projectInfo["projectGUID"] + ".Debug|Any CPU.Build.0 = Debug-"+netTarget+"|Any CPU")
        lines.append("\t\t" + projectInfo["projectGUID"] + ".Release|Any CPU.ActiveCfg = Release-"+netTarget+"|Any CPU")
        lines.append("\t\t" + projectInfo["projectGUID"] + ".Release|Any CPU.Build.0 = Release-"+netTarget+"|Any CPU")
    return lines
def GetProjectDefinitionLines(projectInfo):
    lines = []
    lines.append("Project(\"{}\") = \"{}\", \"{}\", \"{}\"".format(projectInfo["projectTypeGUID"],
                                                                   projectInfo["projectName"],
                                                                   projectInfo["projectRelativePath"],
                                                                   projectInfo["projectGUID"]))
    lines.append("EndProject")
    return lines
    
# Create sln file content
# complete or create each section of the file

# SolutionConfigurationPlatforms
solutionConfigurationSection = globalSectionDict["SolutionConfigurationPlatforms"]
newLines = []
newLines.append(solutionConfigurationSection["Lines"][0])
newLines.append("\t\tDebug|Any CPU = Debug|Any CPU")
newLines.append("\t\tRelease|Any CPU = Release|Any CPU")
newLines.append(solutionConfigurationSection["Lines"][-1])
solutionConfigurationSection["Lines"] = newLines

# ProjectsConfigurationPlatforms
projectsConfigurationSection = globalSectionDict["ProjectConfigurationPlatforms"]
newLines = []
newLines.append(projectsConfigurationSection["Lines"][0])
for project in projectDict.values():
    if not project["isFolder"]:
        newLines.extend(GetProjectConfigurationLines(project))
newLines.append(projectsConfigurationSection["Lines"][-1])
projectsConfigurationSection["Lines"] = newLines

# NestedProjects
if "NestedProjects" in globalSectionDict:
    nestedConfig = globalSectionDict["NestedProjects"]
    newLines = []
    newLines.append(nestedConfig["Lines"][0])
    for project in projectDict.values():
        if not project["isFolder"]:
            newLines.append("\t\t{} = {}".format(project["projectGUID"], project["parentFolderGUID"]))
    newLines.append(nestedConfig["Lines"][-1])
    nestedConfig["Lines"] = newLines

# file header:
newSolutionLines = headerLines[:]

# add projects definition lines
for project in projectDict.values():
    newSolutionLines.extend(GetProjectDefinitionLines(project))
        
newSolutionLines.append("Global")

for section in globalSectionDict.values():
    newSolutionLines.extend(section["Lines"])

newSolutionLines.append("EndGlobal\n")

# finaly write the whole sln file

common.writeFile(solutionPath, '\n'.join(newSolutionLines))

input("Press any key to exit...\n")


















    