import obbinstall
import sys, os.path
from Python import common
import xml.etree.ElementTree as ET

sourcePath = r"D:\Ohbibi\Git\Fps_Android\Unity\Assets\StreamingAssets\UI\Debug.obw"
prefix = [ "Skin" ]
destPath = r"D:\Ohbibi\Git\Fps_Android\Unity\Assets\StreamingAssets\UI\Debug-2.obw"
destEncoding = 'utf-8'

raw = common.readFile(sourcePath)
arrayOfContainer = ET.fromstring(raw.encode('utf-16'))
arrayToExport = []
arrayToKeep = []

for child in arrayOfContainer:
    found = False
    for p in prefix:
        if p in child.get('id'):
            arrayToExport.append(child)
            found = True
            break
    if not found:
        arrayToKeep.append(child)
        
if os.path.exists(destPath):
    
    raw = common.readFile(destPath)
    arrayOfContainer = ET.fromstring(raw.encode('utf-16'))
    
    for child in arrayOfContainer:
        found = False
        for toExport in arrayToExport:
            if toExport.get('id') == child.get('id'):
                found = True
                break
        if not found:
            arrayToExport.append(child)
      
      
def saveFile(path, arrayToWrite):
    with open(path, "w", encoding=destEncoding) as f:
        f.write('<?xml version="1.0" encoding="utf-16"?>\n<ArrayOfContainer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n  ')
        for child in arrayToWrite:
            xml_str = ET.tostring(child, encoding=destEncoding, method='xml').decode(destEncoding)
            f.write(xml_str)
        f.write('</ArrayOfContainer>')
        
saveFile(destPath, arrayToExport)

saveFile(sourcePath, arrayToKeep)
