#!/usr/bin/python
# takes 2 arguments: package path and extract destination path

import sys
import obbinstall
import time
from Python import common


def isDeviceBlackScreen(deviceID):
	mHoldingDisplaySuspendBlocker = ""
	mHoldingWakeLockSuspendBlocker = ""
	if common.isWindowsOS():
		mHoldingDisplaySuspendBlocker = common.shellExecute("adb -s "+deviceID+" shell dumpsys power | findstr mHoldingDisplaySuspendBlocker=false", quiet=True)
		mHoldingWakeLockSuspendBlocker = common.shellExecute("adb -s "+deviceID+" shell dumpsys power | findstr mHoldingWakeLockSuspendBlocker=false", quiet=True)
	elif common.isMacOS():
		mHoldingDisplaySuspendBlocker = common.shellExecute("adb -s "+deviceID+" shell dumpsys power | grep mHoldingDisplaySuspendBlocker=false", quiet=True)
		mHoldingWakeLockSuspendBlocker = common.shellExecute("adb -s "+deviceID+" shell dumpsys power | grep mHoldingWakeLockSuspendBlocker=false", quiet=True)
	print(mHoldingDisplaySuspendBlocker);
	print(mHoldingWakeLockSuspendBlocker);
	return "mHoldingDisplaySuspendBlocker=false" in mHoldingDisplaySuspendBlocker and "mHoldingWakeLockSuspendBlocker=false" in mHoldingWakeLockSuspendBlocker

def isDeviceDisplayReady(deviceID):
	mDisplayReady = ""
	if common.isWindowsOS():
		mDisplayReady = common.shellExecute("adb -s "+deviceID+" shell dumpsys power | findstr mDisplayReady=true", quiet=True)
	elif common.isMacOS():
		mDisplayReady = common.shellExecute("adb -s "+deviceID+" shell dumpsys power | grep mDisplayReady=true", quiet=True)
	return "mDisplayReady=true" in mDisplayReady
	
def unlockAndroidPhone(deviceID):
	
	while not isDeviceDisplayReady(deviceID): #wait until device is ready (if not, isDeviceBlackScreen might give unconsistent return)
		time.sleep(1);
	if isDeviceBlackScreen(deviceID):
		common.shellExecute("adb -s "+deviceID+" shell input keyevent 26", quiet=True) # press power button
	common.shellExecute("adb -s "+deviceID+" shell input touchscreen swipe 130 880 530 380", quiet=True) # swipe up
	

if __name__ == "__main__":
	unlockAndroidPhone(sys.argv[1])