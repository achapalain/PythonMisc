#!/usr/bin/python

import sys, collections, traceback, json
from os.path import *
import xmltodict
import obbinstall
import Python.common as common, Python.unity as unity
from Python.gameSettings import *

def runUnitTests(unityPath, args=[]):
    gameSettings = GameSettings()
    resultsPath = normpath(join(unityPath, "unity_unittests_results.xml"))
    logPath = normpath(join(unityPath, "unityLog.txt"))
    filteredAssemblies = normpath(join(unityPath, "Library/ScriptAssemblies/Assembly-CSharp-Editor.dll")).replace("\\", "/")
    args.append("-testResults " + resultsPath + " -testPlatform editmode -testFilter \"" + filteredAssemblies + "\"")
    res = unity.process(unityPath, args=args,
                        logFile=logPath,
                        autoQuit=False,
                        unityVersion=gameSettings.Project.unityVersion,
                        unitTests=True)
    if res == 0:
        print("UnitTest ran successfully")
        if exists(resultsPath):
            print(resultsPath + " created.")
            # Add a rootNode called <test-run> to have a valid NUnit3 output file.
            fileText = common.readFile(resultsPath)
            fileText = fileText.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<test-run>")
            fileText += "\n</test-run>"
            common.writeFile(resultsPath, fileText)

def formatXmlToHtml(xmlFilePath):
    '''Very basic but functional digest txt formating'''
    rawXml = common.readFile(xmlFilePath)
    dictXml = xmltodict.parse(rawXml)
    
    # print(json.dumps(dictXml,
                     # default=lambda o: o.__dict__, 
                     # sort_keys=True,
                     # indent="\t"))
    visibleAttributes = ["result", "fullname", "message", "stack-trace"]
    def strIndent(indent):
        return ('\t' * indent)
    def printTestSuites(data, indent=0):
        if isinstance(data, dict):
            for k, v in data.items():
                if not isinstance(v, str):
                    if "test-suite" in k:
                        displayTestSuite(v, indent + 1)
                    printTestSuites(v, indent + 1)
        elif isinstance(data, list):
            for e in data:
                printTestSuites(e, indent+1)
    def displayFailureCause(failureCause, indent=0):
        message = failureCause["message"]
        stackTrace = failureCause["stack-trace"].split('\n')
        stackTrace = '\n'.join([strIndent(indent) + line for line in stackTrace])
        print(strIndent(indent) + message + "\n" + stackTrace)
        
    def displayTestCase(testCase, indent=0):
        def displayTestCase_impl(testCase):
            print('')
            print(strIndent(indent) + testCase["@fullname"] + " - " + testCase["@result"])
            if "failure" in testCase:
                displayFailureCause(testCase["failure"], indent + 1)
        if isinstance(testCase, list):
            for e in testCase:
                displayTestCase_impl(e)
        else:
            displayTestCase_impl(testCase)
    def displayTestSuite(testSuite, indent=0):
        def displayTestSuite_impl(testSuite):
            print('')
            print(strIndent(indent) + testSuite["@fullname"] + " - " + testSuite["@result"])
            if "test-case" in testSuite:
                displayTestCase(testSuite["test-case"], indent + 1)
        if isinstance(testSuite, list):
            for e in testSuite:
                displayTestSuite_impl(e)
        else:
            displayTestSuite_impl(testSuite)
    printTestSuites(dictXml)

if len(sys.argv) > 0 and sys.argv[0] == __file__:
    try:
        # Find nearest StreamingAssets dir
        unityPath = None
        streamingAssetsPath = None
        parsedPath = abspath(dirname(__file__))
        for i in range(5):
            localUnityPath = join(parsedPath, "Unity")
            if exists(localUnityPath):
                unityPath = localUnityPath
            parsedPath = dirname(parsedPath)

        def exitLoop():
            exit()

        def runUnitTestsCommand():
            runUnitTests(unityPath)
        
        def runUnitTestsFailureCommand():
            runUnitTests(unityPath, ["-forceTestFail"])
            
        def formatLastResultsCommand():
            resultsPath = normpath(join(unityPath, "unity_unittests_results.xml"))
            formatXmlToHtml(resultsPath)

        actions = collections.OrderedDict([
            (exitLoop, "Exit"),
            (runUnitTestsCommand, "Run Tests"),
            (runUnitTestsFailureCommand, "Run Tests Failure"),
            (formatLastResultsCommand, "Format last results"),
        ])

        def loopChoices(commandName = ""):

            if commandName == "":
                res = common.askChoice("(%s) Select action:" % (unityPath), actions)
            else:
                res = list(actions.keys())[list(actions.values()).index(commandName)]
            res()


        if len(sys.argv) > 1:
            loopChoices(sys.argv[1])
        else:
            while True:
                loopChoices()

    except Exception as e:
        print("UnitTest Exception: " + str(e))
        print(traceback.format_exc())
