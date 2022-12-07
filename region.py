import sys
import os
import mmap
import xml.etree.ElementTree as ET

def getSerial(file):
    serial = ''
    with open(file, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)
        offset = mm.find(b'\x43\x54\x52') #CTR
        if (offset == -1):
            serial = 'Not found'
        else:
            mm.seek(offset+6)
            code = mm.read(4).decode('utf-8')
            serial = 'CTR-' + code
    return serial

def renameFile(existingName, region):
    nameWithoutExtension = existingName[:-4]
    extension = existingName[-4:]
    newName = f'{nameWithoutExtension} ({region}){extension}'
    os.rename(existingName, newName)

def shouldProcessFile(file):
    if not os.path.isfile(file): return False
    if (not file[-3:] == '3ds') and (not file[-3:] == 'cia'): return False
    if file[-8:-5] in {'USA', 'EUR', 'JPN'}: return False
    return True

def main():
    # Parse command line arguments for optional directory (containing 3ds/cia files)
    directory = '.'
    if (len(sys.argv) > 2):
        print('Usage: region.py [folderpath]')
        return
    elif (len(sys.argv) == 2):
        directory = sys.argv[1]

    # Get serial to region mappings from xml
    serialToRegion = {}
    mytree = ET.parse('3dsreleases.xml')
    root = mytree.getroot()
    for child in root:
        serial = ''
        region = ''
        for releaseInfo in child:
            if (releaseInfo.tag == 'serial'): serial = releaseInfo.text
            if (releaseInfo.tag == 'region'): region = releaseInfo.text
        serialToRegion[serial] = region

    # Loop through all 3ds files in directory
    files = os.listdir(directory)
    for file in files:
        filepath = os.path.join(directory, file)
        if shouldProcessFile(filepath):
            print (f'Processing {file}')
            serial = getSerial(filepath)
            if (serial in serialToRegion):
                region = serialToRegion[serial]
                renameFile(filepath, region)
            else:
                print(f'Cannot determine region for {file}')

main()