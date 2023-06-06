#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, platform, shutil, stat, time, platform, signal, subprocess, copy, zipfile, ctypes, collections, re, json, select

# from win32api import GetFileVersionInfo, LOWORD, HIWORD

import os

def getPythonExe():
    def findPythonExe(startDir):
        if not os.path.exists(startDir):
            return None
        for dirPath in os.listdir(startDir):
            subDir = os.path.join(startDir, dirPath)
            if dirPath.lower().startswith("python"):
                path = os.path.normpath(os.path.join(subDir, "python.exe"))
                if os.path.exists(path):
                    print("Using", path)
                    return path
                path = findPythonExe(subDir)
                if path:
                    return path
             
    searchPaths = [
        "c:/",
        os.path.join(getUserFolder(), "AppData/Local/Programs/"),
    ]
    for path in searchPaths:
        pythonPath = findPythonExe(path)
        if pythonPath:
            return pythonPath

def isPython2():
    return sys.version_info.major == 2

def isPython3():
    return sys.version_info.major == 3

#===============================================================================
def isMacOS():
    return platform.system() == 'Darwin'

def isWindowsOS():
    return platform.system() == 'Windows'

def getUserName():
    #Not a perfect way, but it will success with standard users
    userhome = os.path.expanduser('~')          
    return os.path.split(userhome)[-1]

def getUserFolder():
    return os.path.expanduser('~')
    
def getDocumentsFolder():
    return os.path.join(getUserFolder(), "Documents")

def getDesktopFolder():
    return os.path.join(getUserFolder(), "Desktop")

def getVariable(varName, defaultValue, additionalSource, throw=False):
    # Ensure variables exists in local/global/environment context, and convert it to match defaultValue type
    val = defaultValue
    if varName in additionalSource:
        val = additionalSource[varName]
    elif varName in globals():
        val = globals().get(varName)
    elif varName in os.environ:
        val = os.environ.get(varName)
    elif throw:
        raise Exception(varName + " not found.")
            
    return str2type(val, defaultValue)

#===============================================================================

def str2type(value, defaultValue):
    if value == "":
        return defaultValue
    if isinstance(value, str) and not isinstance(defaultValue, str):
        if isinstance(defaultValue, bool):      value = str2bool(value)
        elif isinstance(defaultValue, int):     value = str2int(value)
        elif isinstance(defaultValue, float):   value = str2float(value)
    return value

def str2bool(v):
  return v.lower() in ("yes", "y", "true", "t", "1")

def str2int(v):
    try:
        return int(v)
    except ValueError:
        return 0

def str2float(v):
    try:
        return float(v)
    except ValueError:
        return 0.0

#===============================================================================

def non_block_read(output):
    import fcntl
    
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    if output:
        try:
            return output.readline()
        except:
            return ""
    return ""
        
def shellExecute(cmd, _cwd=None, quiet=False, ignoreOutput=False):
    if ignoreOutput:
        print("shellExecute '" + cmd + "'")
        shellProcess = subprocess.Popen(cmd, shell=True, cwd=_cwd, stdout=subprocess.DEVNULL)
        return None
    else:
        shellProcess = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=_cwd)
        stdout = []
        while True:
            if isWindowsOS():
                output = shellProcess.stdout.readline()
            else:
                output = non_block_read(shellProcess.stdout)
                
            if isPython3():
                if isWindowsOS():
                    output = output.decode("windows-1252")
                    output = output[:-1]
                else:
                    output = output.decode("utf-8")

            stdout.append(output)
            if not quiet and output != '':
                print(output)
            if (output == '' or output == None) and shellProcess.poll() != None:
                break
        return ''.join(stdout)

def shellExec(cmd, _cwd=None, quiet=False, isShell=True):
    """
    :return: (errorCode, executionLog)
    """
    if isinstance(cmd, list) and not quiet:
        if len(cmd) > 0:
            print(cmd[0])
        if len(cmd) > 1:
            print("\t" + "\n\t".join([str(x) for x in cmd[1:]]))
    shellProcess = subprocess.Popen(cmd, shell=isShell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=_cwd)
    stdout = []
    while True:
        if isWindowsOS():
            output = shellProcess.stdout.readline()
        else:
            output = non_block_read(shellProcess.stdout)
        #shellProcess.stdout.flush()
        if isPython3():
            if isWindowsOS():
                try:
                    output = output.decode("windows-1252")
                    while len(output) > 0 and output[-1:] in ["\r", "\n"]:
                        output = output[:-1]
                except:
                    output = None
            else:
                output = output.decode("utf-8")
                if output.endswith("\n"):
                    output = output[:-1]
 
        if output != None and output != '':
            stdout.append(output)
            if not quiet:
                try:
                    print(getAsciiText(output))
                except UnicodeEncodeError:
                    import traceback
                    print(traceback.format_exc())
        if (output == '' or output == None) and shellProcess.poll() != None:
            break
    return shellProcess.returncode, "\n".join(stdout)

def shellExecuteInDir(cmd, params=None):
    cmd = cmd.replace('/', '\\')
    parts = cmd.rpartition('\\')
    dir = None
    exe = None
    if parts[1] == '':
        exe = cmd
    else:
        dir = parts[0]
        exe = parts[2]
    if params == None:
        params = ''

    print('> ' + cmd + ' ' + params)
    p = subprocess.Popen(exe + ' ' + params, shell=True, cwd=dir)
    p.wait()

def executeFile(filePath):
    with open(filePath) as f:
        code = compile(f.read(), filePath, 'exec')
        return exec(code)

#===============================================================================

COPY_OPTION_NONE = ""
COPY_OPTION_REPLACE = "ReplaceFiles"
COPY_OPTION_MERGE = "MergeFiles"
COPY_OPTION_MERGE_REPLACE = "MergeFilesAndReplace"

def removeData(filePaths, throwFileNotFound=True):
    if isinstance(filePaths, str):
        filePaths = [filePaths]
    for path in filePaths:
        try:
            if not os.path.exists(path):
                continue
            if isWindowsOS():
                os.chmod(path, stat.S_IWUSR)
            elif isMacOS():
                os.chmod(path, stat.S_IRWXU)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path, ignore_errors=True)
        except FileNotFoundError:
            pass

def deleteData(filePaths):
    removeData(filePaths)
    
def deleteFile(filePaths):
    removeData(filePaths)
    
def deleteFolder(filePaths):
    removeData(filePaths)
    
def moveData(src, dst, copyOption=COPY_OPTION_REPLACE):
    if not os.path.exists(src):
        print("Source path does not exist: " + src)
        return False
        
    copyData(src, dst, copyOption)
    removeData(src)
    return True

def copyData(src, dst, copyOption=COPY_OPTION_REPLACE):
    def mergeTree(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.normpath(os.path.join(src, item))
            d = os.path.normpath(os.path.join(dst, item))
            if os.path.isdir(s):
                mergeTree(s, d, symlinks, ignore)
            elif copyOption == COPY_OPTION_MERGE_REPLACE or not os.path.exists(d):
                ensureDirectoryExists(os.path.dirname(d))
                shutil.copy2(s, d)

    if not os.path.exists(src):
        return False
    if os.path.exists(dst):
        os.chmod(dst, stat.S_IWUSR)
        if copyOption == COPY_OPTION_NONE:
            return False
        elif copyOption == COPY_OPTION_REPLACE:
            removeData(dst)

    targetDir = os.path.dirname(dst)
    if targetDir != dst and targetDir != "":
        ensureDirectoryExists(targetDir)
        
    if os.path.isfile(src):
        shutil.copy(src, dst)
    else:
        # folder behaviour
        if os.path.exists(dst) and "MergeFiles" in copyOption:
            mergeTree(src, dst)
        else:
            shutil.copytree(src, dst)
    return True
    
    
def ensureDirectoryExists(path):
    if not os.path.lexists(path):
        endProcess = False
        while not endProcess:
            try:
                os.makedirs(path, exist_ok=True)
                endProcess = True
            except PermissionError as e:
                pass
            except:
                endProcess = True

def isDirectory(path, throwError=False):
    if os.path.isdir(path):
        return True
    elif throwError:
        raise Exception("Invalid directory: " + path)
    else:
        return False

# Delete a directory recursively. Will delete itself if needed.
# Use force=True for more efficiency (avoid error on corrupted files)
def clearDirectory(src, deleteRoot=False, force=False):

    def forceDeleteDirectory(src):
        if isWindowsOS():
            os.system("del /f " + src)
        else:
            os.system("rm -rf " + src)
            
    if deleteRoot and force:
        forceDeleteDirectory(src)
        return
    if not os.path.isdir(src):
        return
        
    if not os.access(src, os.R_OK | os.W_OK) and not isWindowsOS():
        os.chmod(src, stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)
    names = os.listdir(src)
    for name in names:
        srcName = os.path.join(src, name)
        if force:
            forceDeleteDirectory(srcName)
            continue
        if os.path.isdir(srcName):
            clearDirectory(srcName, True)
        elif os.path.isfile(srcName):
            os.chmod(srcName, stat.S_IWUSR)
            os.remove(srcName)
        else: # probably symlink
            os.remove(srcName)

    if deleteRoot:
        os.chmod(src, stat.S_IWUSR)
        os.rmdir(src)

def getFileCreationDate(filePath):
    if isMacOS():
        return os.stat(filePath).st_birthtime
    elif isWindowsOS():
        os.path.getctime(filePath)
    else:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return os.stat(filePath).st_mtime

def getCommonRoot(*args):
    if len(args) == 0:
        return ""
    elif len(args) == 1:
        return args[0]

    pathList = []

    for argIdx in range(len(args)):
        pathList.append(args[argIdx].replace("\\", "/"))

    minLen = len(pathList[0])
    for argIdx in range(len(pathList)):
        if len(pathList[argIdx]) < minLen:
            minLen = len(pathList[argIdx])

    result = ""

    for charIdx in range(minLen):
        currentChar = pathList[0][charIdx]
        for arg in pathList:
            if arg[charIdx] != currentChar:
                return result
        result += currentChar

    return result


#def GetVersionNumber(filename):
#    #!!! win32api needed
#    try:
#        info = GetFileVersionInfo(filename, "\\")
#        ms = info['FileVersionMS']
#        ls = info['FileVersionLS']
#        return HIWORD (ms), LOWORD (ms), HIWORD (ls), LOWORD (ls)
#    except:
#        return 0,0,0,0

#===============================================================================
def zipData(pathIn, pathOut, compression=zipfile.ZIP_DEFLATED):
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    zipf = zipfile.ZipFile(pathOut, "w", compression)
    zipdir(pathIn, zipf)
    zipf.close()

#===============================================================================
def getAsciiText(text):
    return text.encode('ascii', 'ignore').decode('utf8')

def readAsciiFileLines(filePath):
    encodings = ["utf8", "latin"]
    res = []
    for enc in encodings:
        try:
            logFileF = open(filePath, encoding=enc)
            lines = logFileF.readlines()
            logFileF.close()
            for line in lines:
                res.append(line.replace("\r", "").replace("\n", "").encode('ascii', 'ignore').decode('utf8'))
            break
        except:
            pass
    return res
    
def readAsciiFile(filePath):
    return "".join(readAsciiFileLines(filePath))
    
def printLines(lines, fd=None):
    if not fd:
        fd = sys.stdout
    for line in lines:
        if not isWindowsOS():
            select.select([], [fd.fileno()], [], 5)
        print(line, file=fd)
        fd.flush()
        
def safeFlush(filedescriptor):
    select.select([], [filedescriptor.fileno()], [], 5)
    filedescriptor.flush()
    

#===============================================================================
def pause(text=None):
    if text:
        print(text)
    if isWindowsOS():
        os.system("pause")
    else:
        print("'pause' function not tested on this OS")
        os.system('read -p "Press any key to continue"')

def waitForKey(text=None):
    if text:
        print(text)
    if isWindowsOS():
        #Doesn't work on IDLE
        import msvcrt
        return msvcrt.getch()
    else:
        print("'waitForKey' function not implemented on this OS")

def waitForInput(text=None):
    if not text:
        text = "Waiting for input ..."
    print(text)
    return sys.stdin.read(1)

def waitForText(text=None):
    if text:
        print(text)
    return input()

def askYesNo(text):
    res = input(text)
    if not res or res == '' or (isinstance(res, str) and res.lower() == 'n'):
        return False
    else:
        return True

# listChoices: can be either list or dictionary
def askChoice(title, listChoices, allowMultiChoice=False, allowNoChoice=True):
    if title:
        print(title)
    choices = []
    if isinstance(listChoices, dict):
        for key in listChoices:
            choices.append((key, listChoices[key]))
    elif isinstance(listChoices, list):
        for i in range(len(listChoices)):
            choices.append((i, listChoices[i]))
    for i in range(len(choices)):
        print("{} - {}".format(i, choices[i][1]))

    res = str(input("Choice(s): "))
    res = res.split()
    resTable = []
    for v in res:
        resTable.append(choices[int(v)][0])
    if not allowNoChoice:
        if len(resTable) == 0:
            resTable.append(choices[0][0])
    elif allowNoChoice and len(resTable) == 0:
        return None
    if not allowMultiChoice:
        if len(resTable) > 0:
            resTable = resTable[0]
        else:
            resTable = ''
    return resTable


def printTitle(*text):
    text = " ".join([str(x) for x in text])
    print('#### ' + text + ' ####')

def browseForFile(initialDir = "/", fileTypes = (("text files", "*.txt"), ("all files", "*.*"))):

    from tkinter import filedialog
    from tkinter import Tk

    root = Tk()
    root.filename =  filedialog.askopenfilename(initialdir = initialDir, title = "Select file",filetypes = fileTypes)
    return root.filename

#===============================================================================
def isEmpty(val):
    return val == None or val == '' or val == [] or val == {}

def sortDictKeys(data):
    if isinstance(data, dict):
        keys = [x for x in data]
        keys.sort()
        res = collections.OrderedDict()
        for key in keys:
            res[key] = sortDictKeys(data[key])
    elif isinstance(data, list):
        res = []
        for x in data:
            res.append(sortDictKeys(x))
    else:
        res = data
    return res

# Usage : 
# >>> Numbers = enum(ONE=1, TWO=2, THREE='three')
# >>> Numbers.ONE
# 1
# >>> Numbers.THREE
# 'three'
def enumValues(**enums):
    return type('Enum', (), enums)

# Usage
# >>> Numbers = enum('ZERO', 'ONE', 'TWO')
# >>> Numbers.ONE
# 1
# >>> Numbers.reverse_mapping['three']
# 'THREE'
def enumList(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

FILTERCHECK_START = 1
FILTERCHECK_ALL = 2
FILTERCHECK_END = 3
def hasFilter(val, filters, noCase=True, check=FILTERCHECK_ALL):
    if noCase:
        val = val.lower()
    for f in filters:
        if noCase:
            f = f.lower()
        if check == FILTERCHECK_START:
            if val.startswith(f):
                return True
        elif check == FILTERCHECK_END:
            if val.endswith(f):
                return True
        else:
            if f in val:
                return True
        

def printDebug(val, indent=0):
    indentSpace = ""
    for i in range(indent):
        indentSpace = indentSpace + "\t"
    if isinstance(val, list):
        for v in val:
            printDebug(v, indent + 1)
    elif isinstance(val, dict):
        for key in val:
            print(indentSpace, key)
            printDebug(val[key], indent + 1)
    else:
        print(indentSpace, val)

def forceStrUnicode(str):
    return ''.join([i if ord(i) < 128 else ' ' for i in str])

#===============================================================================
def logObjectsDiff(objLeft, objRight):
    xId = objLeft["ID"]
    yId = objRight["ID"]

    def compareSubObj(path, x, y):
        printedPath = xId + " - " + ".".join(path)
        if type(x) != type(y):
            print(printedPath, "*", type(x), "VS", type(y))
        elif isinstance(x, dict):
            xKeys = [key for key in x]
            yKeys = [key for key in y]
            keys = set(xKeys + yKeys)
            for key in keys:
                if   key not in x:  print(printedPath, "*", key + " not in " + xId)
                elif key not in y:  print(printedPath, "*", key + " not in " + yId)
                else:               compareSubObj(path + [key], x[key], y[key])
        elif isinstance(x, list):
            for i in range(max(len(x), len(y))):
                if   i >= len(x): print(printedPath + "." + str(i), "*", xId + " doesn't exist")
                elif i >= len(y): print(printedPath + "." + str(i), "*", yId + " doesn't exist")
                else:             compareSubObj(path + [str(i)], x[i], y[i])
        else:
            if x != y:  print(printedPath, "*", x, "/", y)
    compareSubObj([], objLeft, objRight)

#===============================================================================
def getFileParts(filepath):
    dirpath, filename = os.path.split(filepath)
    filename, ext = os.path.splitext(filename)
    res = (dirpath, filename, ext)
    return res

def getFiles(path, restrictedExtension=None, excludedExtension=None, onlyDirs=False, onlyFiles=False, recursive=True, searchString=None):
    def checkExtensionList(ext):
        if ext == None:
            return
        if isinstance(ext, str):
            ext = [ext.lower()]
        elif isinstance(ext, list):
            for i in range(len(ext)):
                ext[i] = ext[i].lower()
        return ext

    restrictedExtension = checkExtensionList(restrictedExtension)
    excludedExtension = checkExtensionList(excludedExtension)

    res = []
    def addFile(f):
        (root, filename, ext) = getFileParts(f)
        ext = ext.lower()
        if excludedExtension is not None and ext in excludedExtension:
            return
        if restrictedExtension is not None and ext in restrictedExtension:
            res.append(f)
        elif restrictedExtension is None:
            if searchString is None or searchString in f:
                res.append(f)

    if os.path.isfile(path):
        addFile(path)
    else:
        for dirpath, dirnames, filenames in os.walk(path):
            if not onlyDirs:
                for f in filenames:
                    addFile(os.path.normpath(os.path.join(dirpath, f)))
            if not onlyFiles:
                for d in dirnames:
                    addFile(os.path.normpath(os.path.join(dirpath, d)))
            if not recursive:
                break;
    return res

def pathContains(path, part):
    part = os.path.normpath(part).replace(os.sep, '/').lower()
    path = os.path.normpath(path).replace(os.sep, '/').lower()
    
    if part.endswith('/'):
        part = part[0: len(part) - 1]
        
    if part.startswith('/'):
        part = part[1:]
        
    if path.endswith('/'):
        path = path[0: len(path) - 1]
        
    if path.startswith('/'):
        path = path[1:]
    
    if not part in path:
        return False
    
    split_path = path.split('/')
    split_part = part.split('/')
    count = len(split_part)
    part_index = 0
    for folder in split_path:
        if split_part[part_index] == folder:
            part_index += 1
            
        if part_index == count:
            return True
            
    return False

#===============================================================================
def readFile(filePath, fileEncoding="", throwExceptions=False):
    try:
        if fileEncoding != "":
            with open(filePath, "r", encoding=fileEncoding) as f:
                return f.read().encode(fileEncoding).decode(fileEncoding)
        with open(filePath, "r") as f:
            return f.read()
    except Exception as e:
        if not throwExceptions:
            import traceback
            traceback.print_exc()
        else:
            raise
    return None

def writeFile(filePath, content):
    ensureDirectoryExists(os.path.dirname(filePath))
    if isinstance(content, bytes):
        with open(filePath, "wb") as f:
            f.write(content)
    else:
        with open(filePath, "w") as f:
            f.write(content)

def appendFile(filePath, content):
    option = "a" if os.path.exists(filePath) else "w"
    with open(filePath, option) as f:
        return f.write(content)

# fnLineReplacement: function that takes as parameter the current line and return the parsed result
def replaceLineInFile(filepath, fnLineReplacement):
    pathIn = filepath
    pathOut = filepath + '.tmp'
    with open(pathOut, "w") as fout:
        with open(pathIn, "r") as fin:
            for line in fin:
                line = fnLineReplacement(line)
                fout.write(line)
    removeData(pathIn)
    os.rename(pathOut, pathIn)

def replaceInFile(filepath, replacementDict, useRegex=False):
    with open(filepath) as f:
        data = f.read()
        encoding = f.encoding
    dataBackup = copy.deepcopy(data)
    for key in replacementDict:
        if not useRegex:
            data = data.replace(key, replacementDict[key])
        else:
            # TODO
            # regex = re.compile(key)
            # if re.search(regex, data):
            pass
    if dataBackup != data:
        with open(filepath, "w", encoding=encoding) as f:
            f.write(data)


def createFile(filepath, content="", encoding="utf8"):
    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)


#===============================================================================
def getSvnVersionOfFile(svnExeDir, filename):
    #cmd = '%s\svn info %s | grep "Last Changed Rev" ' % (svnExeDir, filename)
    cmd = '%s\svn info %s' % (svnExeDir, filename)
    lines = os.popen(cmd, "r").readlines()
    for line in lines:
        line = line.replace('\n', '')
        newline = line.replace("Last Changed Rev: ", "")
        if newline != line:
            return int(newline)

#===============================================================================
def isProcessRunning(processName, caseSensitive=False):
    """ Test if a process or sub process is running. Test is not case sensitive and no need to precise process extension.
    :param processName: MainProcess[/SubProcess]. Ex: "Python/OBB Localization"
    """
    if not caseSensitive:
        processName = processName.lower()
    processTree = processName.split("/")

    output = None
    if isWindowsOS():
        processRoot = processTree[0]
        if not processRoot.endswith(".exe"):
            processRoot += ".exe"
        _, output = shellExec('tasklist.exe /v /fo csv /fi "IMAGENAME eq {}"'.format(processRoot), quiet=True)
    elif isMacOS():
        _, output = shellExec(['ps', '-A'], quiet=True)
    else:
        print("TODO 'isProcessRunning' for platform " + platform.system())

    if not caseSensitive:
        output = output.lower()
    lines = output.split("\n")
    for line in lines:
        found = True
        for subProcess in processTree:
            if subProcess not in str(line):
                found = False
                break
        if found:
            return True

    return False

def killProcess(processName):
    if isWindowsOS():
        import ctypes, csv
        if not processName.endswith(".exe"):
            processName += ".exe"
        processName = processName.lower()

        def kill(pid):
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(1, 0, pid)
            return (0 != kernel32.TerminateProcess(handle, 0))
        
        tasklist = subprocess.Popen('tasklist.exe /fo csv', stdout=subprocess.PIPE, universal_newlines=True)
        pidValues = []
        for task in csv.DictReader(tasklist.stdout):
            for key in task:
                if task[key].lower() == processName:
                    pid = int(task["PID"])
                    kill(pid)
                    break
            
    elif isMacOS():
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        for line in out.splitlines():
            line = line.decode("utf-8")
            if processName in line:
                pid = int(line.split(None, 1)[0])
                os.kill(pid, signal.SIGKILL)

def startSilentThread(runFn, *args):
    import threading
    t = threading.Thread(target=runFn, args=args)
    t.daemon = True
    t.start()
    return t


def waitEndOfActions(actions, timeOut = 60):
    '''
    :param actions: A sequence of [function, arg0, arg1, ...]
    '''
    threads = []
    for action in actions:
        threads.append(startSilentThread(*action))

    waitTime = 0.05
    totalWaitTime = 0
    while totalWaitTime < timeOut and len(threads) > 0:
        for t in reversed(threads):
            if t.isAlive():
                totalWaitTime += waitTime
                time.sleep(waitTime)
            else:
                threads.remove(t)
    if len(threads) == 0:
        return True
    else:
        # Timeout was reached
        return False

#===============================================================================
class Timer:
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.start()

    def __repr__(self):
        return "Timer - " + self.formatedDuration()

    def __str__(self):
        return self.formatedDuration()

    def start(self):
        self.startTime = time.time()
        self.endTime = None

    def stop(self):
        if self.startTime != None and self.endTime == None:
            self.endTime = time.time()
        return self.getDuration()

    def getDuration(self):
        if self.startTime != None:
            if self.endTime != None:
                return self.endTime - self.startTime
            else:
                return time.time() - self.startTime
        else:
            return 0

    def formatedDuration(self):
        res = ""
        duration = self.getDuration()
        duration = int(duration)

        if duration <= 0:
            return "0s"

        s = duration % 60
        res = str(s) + "s"

        duration = (duration - s) / 60
        m = duration % 60
        if duration > 0:
            res = str(m) + "m " + res

        duration = (duration - m) / 60
        h = duration
        if duration > 0:
            res = str(h) + "h " + res
        return res

#===============================================================================

class Clipboard:
    @staticmethod
    def get():
        # ctypes.windll.user32.OpenClipboard(None) # Open Clip, Default task
        # pcontents = ctypes.windll.user32.GetClipboardData(1) # 1 means CF_TEXT.. too lazy to get the token thingy ...
        # data = ctypes.c_char_p(pcontents).value
        # #gul(pcontents) ?
        # ctypes.windll.user32.CloseClipboard()
        # return data

        CF_TEXT = 1
        kernel32 = ctypes.windll.kernel32
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        user32 = ctypes.windll.user32
        user32.GetClipboardData.restype = ctypes.c_void_p
        user32.OpenClipboard(0)
        try:
            if user32.IsClipboardFormatAvailable(CF_TEXT):
                data = user32.GetClipboardData(CF_TEXT)
                data_locked = kernel32.GlobalLock(data)
                text = ctypes.c_char_p(data_locked)
                value = text.value
                kernel32.GlobalUnlock(data_locked)
                if type(value) is bytes:
                    return value.decode()
                return value
        finally:
            user32.CloseClipboard()

    @staticmethod
    def get_str():
        data = Clipboard.get()
        if isinstance(data, (bytes, bytearray)):
            data = str(data, "utf-8")
        return data

    @staticmethod
    def set(data):
        ctypes.windll.user32.OpenClipboard(None) # Open Clip, Default task
        ctypes.windll.user32.EmptyClipboard()
        hCd = ctypes.windll.kernel32.GlobalAlloc(0x2000, len(bytes(data,"ascii")) + 1) # Global Memory allocation
        pchData = ctypes.windll.kernel32.GlobalLock(hCd)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(data,"ascii"))
        ctypes.windll.kernel32.GlobalUnlock(hCd)
        ctypes.windll.user32.SetClipboardData(1,hCd)
        ctypes.windll.user32.CloseClipboard()

