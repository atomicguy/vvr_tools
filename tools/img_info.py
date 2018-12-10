from __future__ import division, absolute_import

import os
import glob
import json

from lxml import etree
from PIL import Image

def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))

cards = find_filepaths('data/validation_cardinfo', 'xml')

info = []

for card in cards:
    name = os.path.splitext(os.path.basename(card))[0]

    img = Image.open(os.path.join('data', 'validation_set', '{}.jpg'.format(name)))
    
    width, height = img.size

    info.append({'name': name, 'img_size': {'width': width, 'height': height}})

with open(os.path.join('data', 'img_info.json'), 'w') as f:
        json.dump(info, f, indent=2)