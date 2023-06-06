import os, collections, copy, json, traceback
import obbinstall
from Python import common

import Python.jsonUtils as jsonUtils

def getDefaultUserFilePath(scriptPath):
    dirPath, fileName, _ = common.getFileParts(scriptPath)
    return os.path.join(dirPath, fileName + ".user")

class Config():
    def __init__(self):
        self.path = ""

    def load(self, filePath):
        self.path = filePath
        backup = copy.deepcopy(self)
        try:
            if not os.path.exists(filePath):
                return False
            jsonData = open(filePath, encoding = "utf-8")
            if not jsonData:
                return False
            def from_json(json_object):
                if 'fname' in json_object:
                    return FileItem(json_object['fname'])
            jsonDecoder = json.JSONDecoder(object_hook = from_json, object_pairs_hook = collections.OrderedDict)
            res = jsonDecoder.decode(jsonData.read())
            for key in res:
                if key in self.__dict__:
                    self.__dict__[key] = res[key]
            return True
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self = backup

    def save(self, filePath=None):
        if not filePath:   filePath = self.path
        try:
            # Only save if data has changed
            if os.path.exists(filePath):
                data = jsonUtils.load(filePath)
                if data == self.__dict__:
                    return
            jsonUtils.save(self.__dict__, filePath)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
