"""
Inject font assets into scratch as costumes

Created by NicePotato5755
"""

# pylint: disable=C0103, W0105

import time
import hashlib
import pprint
import sys
import zipfile
import json
import string
import os
import shutil
import pathlib
import opentypesvg.fonts2svg as f2s
import svgwrite

pp = pprint.PrettyPrinter(indent=1, depth=1)

DIVIDER = "---------------------------"

PROJECT_INPUT = "PotatoText.sb3"
PROJECT_OUTPUT = "PotatoText-new.sb3"
FONTS_DIR = 'fonts'
FONT_EXTRACT_DIR = 'extracted'
PROJECT_EXTRACT_DIR = 'project'
DEFAULTS_DIR = 'defaults'
PROCCESED_DIR = 'processedGlyphs'

# delete the output project file (.sb3)
if os.path.exists(PROJECT_OUTPUT):
    os.remove(PROJECT_OUTPUT)

# delete old unpacked project directory
if os.path.exists(PROJECT_EXTRACT_DIR):
    shutil.rmtree(PROJECT_EXTRACT_DIR)
os.mkdir(PROJECT_EXTRACT_DIR)

# delete old font extraction
if os.path.exists(FONT_EXTRACT_DIR):
    shutil.rmtree(FONT_EXTRACT_DIR)
os.mkdir(FONT_EXTRACT_DIR)

# delete old processed glyph directory
if os.path.exists(PROCCESED_DIR):
    shutil.rmtree(PROCCESED_DIR)
os.mkdir(PROCCESED_DIR)

"""
Prepare project
"""

print(DIVIDER)
print("Extracting project")

with zipfile.ZipFile(PROJECT_INPUT, 'r') as zip_ref:
    zip_ref.extractall(PROJECT_EXTRACT_DIR)

print("Loading project.json")

with open(PROJECT_EXTRACT_DIR+'/project.json', encoding="utf-8") as f:
    project = json.load(f)

# pts - PotatoText Sprite
pts = None

for sprite in project['targets']:
    if sprite['name'].startswith("PotatoText"):
        pts = sprite

if pts is None:
    print("No valid PotatoText sprite in project!")
    sys.exit(-1)

print("Wiping old costumes")

for costume in pts['costumes']:
    # Get the costume file
    oldFile = PROJECT_EXTRACT_DIR+"/"+costume['md5ext']
    if os.path.exists(oldFile):
        os.remove(oldFile)

pts['costumes'] = []

def importCostume(filePath, costumeName):
    # Open the file in binary mode
    with open(filePath, 'rb') as f:
        # Read the contents of the file
        data = f.read()
    # Calculate the MD5 hash of the file contents
    hash_object = hashlib.md5(data)
    md5_hash = hash_object.hexdigest()
    newFile = md5_hash+pathlib.Path(filePath).suffix
    costume_data = {
        'assetId': md5_hash,
        'md5ext': newFile,
        'name': costumeName,
        'bitmapResolution': 1,
        'dataFormat': 'svg',
        'rotationCenterX': 82,
        'rotationCenterY': 73.5,
    }
    pts['costumes'].append(costume_data)
    shutil.copyfile(filePath, PROJECT_EXTRACT_DIR+"/"+newFile)

print("Importing default costumes")

for subdir, dirs, files in os.walk(DEFAULTS_DIR):
    for image in files:
        if pathlib.Path(image).suffix == ".svg":
            imagePath = subdir+"/"+image
            imageName = os.path.basename(imagePath)
            nameOnly = os.path.splitext(imageName)[0]
            importCostume(imagePath, nameOnly)

print("Importing glyph costumes")

"""
Extract fonts
"""

print(DIVIDER)
print("Extracting Fonts")

# The dictionary that contains character names and their actual character
IMPORT_CHARS = {
    **{"one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
       "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0"},
    **{char.lower(): char for char in string.ascii_lowercase},
    **{char.upper(): char for char in string.ascii_uppercase},
    **{'space': ' ', 'newline': '\n', 'tab': '\t'},
    **{'exclam': '!', 'quotedbl': '"', 'numbersign': '#', 'dollar': '$',
       'percent': '%', 'ampersand': '&', 'quotesingle': "'", 'parenleft': '(',
       'parenright': ')', 'asterisk': '*', 'plus': '+', 'comma': ',',
       'hyphen': '-', 'period': '.', 'slash': '/', 'colon': ':',
       'semicolon': ';', 'less': '<', 'equal': '=', 'greater': '>',
       'question': '?', 'at': '@', 'bracketleft': '[', 'backslash': '\\',
       'bracketright': ']', 'asciicircum': '^', 'underscore': '_', 'grave': '`',
       'braceleft': '{', 'bar': '|', 'braceright': '}', 'asciitilde': '~'},
    **{'AE': 'Æ', 'ae': 'æ', 'OE': 'Œ', 'oe': 'œ', 'Eth': 'Ð', 'eth': 'ð',
       'Thorn': 'Þ', 'thorn': 'þ', 'Wynn': 'Ƿ', 'wynn': 'ƿ',
       'Eng': 'Ŋ', 'eng': 'ŋ', 'Yogh': 'Ȝ', 'yogh': 'ȝ'},
    **{'adieresis': 'ä', 'Adieresis': 'Ä', 'odieresis': 'ö', 'Odieresis': 'Ö',
       'udieresis': 'ü', 'Udieresis': 'Ü', 'szlig': 'ß'}
}

for subdir, dirs, files in os.walk(FONTS_DIR):
    for sub in dirs:
        if sub != "unused":
            extFDir = os.path.join(FONT_EXTRACT_DIR,sub)
            print("in "+extFDir)
            os.mkdir(extFDir)
            for fsubdir, fdirs, ffiles in os.walk(os.path.join(subdir, sub)):
                for font in ffiles:
                    if pathlib.Path(font).suffix == ".ttf" or pathlib.Path(font).suffix == ".otf":
                        print(font)
                        os.mkdir(extFDir+"/"+font)
                        os.mkdir(extFDir+"/"+font+"/b")
                        os.mkdir(extFDir+"/"+font+"/c")
                        f2s.main([os.path.join(subdir, sub, font), '-c', "000000", '-o', extFDir+"/"+font+"/b"])
                        f2s.main([os.path.join(subdir, sub, font), '-c', "ff0000", '-o', extFDir+"/"+font+"/c"])

                        # Begin glyph processing
                        nameOnly = os.path.splitext(font)[0]
                        # Black glyphs
                        glyphPath = extFDir+"/"+font+"/b"
                        start_time = time.time()

                        # Make sure the system aknowledges the newly dumped files before proceeding
                        while not os.path.exists(glyphPath+"/A.svg"):
                            elapsed_time = time.time() - start_time
                            if elapsed_time >= 5:
                                print("Timeout exhausted, possibly corrupt ttf font! Font: "+font)
                                sys.exit('Timeout waiting for file')
                            time.sleep(1)

                        for gsubdir, gdirs, gfiles in os.walk(os.path.join(glyphPath)):
                            for glyph in gfiles:
                                glyphName = os.path.splitext(glyph)[0]
                                if glyphName in IMPORT_CHARS:
                                    importCostume(gsubdir+"/"+glyph, "b→"+nameOnly+"→"+IMPORT_CHARS[glyphName])

"""
Write new project
"""

print("Packing new project")

# replace old project.json
with open(PROJECT_EXTRACT_DIR+'/project.json', 'w', encoding="utf-8") as f:
    json.dump(project, f)

zipf = zipfile.ZipFile(PROJECT_OUTPUT, 'w', zipfile.ZIP_DEFLATED)

# Iterate over all the files in the directory and add them to the zip file
for root, dirs, files in os.walk(PROJECT_EXTRACT_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        # Get the base name of the file (without the directory name)
        file_name = os.path.basename(file_path)
        # Add the file to the zip file with the base name as the second argument
        zipf.write(file_path, file_name)

# Close the ZipFile object
zipf.close()

print("Done!")
