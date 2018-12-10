from __future__ import division, absolute_import

import os
import glob
import json

from lxml import etree

def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))

cards = find_filepaths('data/validation_cardinfo', 'xml')

info = []

for card in cards:
    name = os.path.splitext(os.path.basename(card))[0]

    truth = etree.parse(card)

    card = truth.xpath("//*[local-name()='object']/*[text()='Card']/./..")[0]
    c_xmin = int(card.find('bndbox/xmin').text)
    c_xmax = int(card.find('bndbox/xmax').text)
    c_ymin = int(card.find('bndbox/ymin').text)
    c_ymax = int(card.find('bndbox/ymax').text)

    info.append({'name': name, 'bbox': [c_xmin, c_ymin, c_xmax, c_ymax]})

with open(os.path.join('data', 'gt_info.json'), 'w') as f:
        json.dump(info, f, indent=2)