import obbinstall
from os.path import *
from Python import common, ioUtils, zipUtils

testApkSigner = r"C:\Program Files\Java\jdk1.8.0_25\bin\jarsigner.exe"
testApkDirPath = r"C:\Users\ACHAPALAIN\Downloads\PerfsEval02\FPS-3552-1.5.4-Prod-arm-master.repack"
testKeyStore = r"C:/Ohbibi/Git/Fps2/Unity/Assets/Plugins/Android/FRAG.keystore"
testKeyStorePass = "PH2ZGucdag"
testAlias = "prod"
testAliasPass = "hu4KuB1BuG"

def repackDirectoryToApk():
    # Should we remove?:
    # - META-INF/CERT.RSA
    # - META-INF/CERT.SF

    # Zip directory to an apk
    apkPath = join(testApkDirPath, "..", basename(testApkDirPath) + ".apk")
    ioUtils.remove(apkPath)
    zipUtils.zipData(testApkDirPath, apkPath)

    # Sign apk
    cwd, apkSigner, _ = common.getFileParts(testApkSigner)
    command = basename(testApkSigner)
    cwd = dirname(testApkSigner)
    commandLine = [
        command,
        "-keystore",  '"' + testKeyStore + '"',
        "-storepass",  testKeyStorePass,
        "-keypass",  testAliasPass,
        '"' + apkPath + '"',
        testAlias
    ]
    commandLine = " ".join(commandLine)
    common.shellExec(commandLine, _cwd=cwd)

repackDirectoryToApk()