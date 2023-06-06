import obbinstall
from Framework import common

COPY_OPTION_NONE = common.COPY_OPTION_NONE
COPY_OPTION_REPLACE = common.COPY_OPTION_REPLACE
COPY_OPTION_MERGE = common.COPY_OPTION_MERGE
COPY_OPTION_MERGE_REPLACE = common.COPY_OPTION_MERGE_REPLACE


def remove(filePaths):
    return common.removeData(filePaths)


def move(src, dst, copyOption=COPY_OPTION_REPLACE):
    return common.moveData(src, dst, copyOption=copyOption)


def copy(src, dst, copyOption=COPY_OPTION_REPLACE):
    return common.copyData(src, dst, copyOption=copyOption)


def ensureDirectoryExists(path):
    return common.ensureDirectoryExists(path)


def isDirectory(path, throwError=False):
    return common.isDirectory(path, throwError=throwError)


def clear(src, deleteRoot=False):
    return common.clearDirectory(src, deleteRoot=deleteRoot)


def getCreationDate(path):
    return common.getFileCreationDate(path)
