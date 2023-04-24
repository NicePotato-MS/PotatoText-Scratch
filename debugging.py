import sys
import zipfile
import json
import pprint

pp = pprint.PrettyPrinter(indent=1)

with zipfile.ZipFile('PotatoText.sb3', 'r') as zip_ref:
    with zip_ref.open('project.json') as f:
        data = json.load(f)

# Iterate through the "targets" list to find the sprite
for target in data['targets']:
    if target['name'].startswith('PotatoText'):
        sprite = target
        break

# Do something with the sprite data
if sprite is not None:
    print('Found sprite named "PotatoText..."!')
else:
    print('Could not find sprite named "PotatoText...".')
    sys.exit(-1)