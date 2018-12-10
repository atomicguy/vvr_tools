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

    truth = etree.parse(card)

    card = truth.xpath("//*[local-name()='object']/*[text()='MAIP']/./..")[0]
    xmin = int(card.find('bndbox/xmin').text)
    xmax = int(card.find('bndbox/xmax').text)
    ymin = int(card.find('bndbox/ymin').text)
    ymax = int(card.find('bndbox/ymax').text)

    img = Image.open(os.path.join('data', 'validation_set', '{}.jpg'.format(name)))
    cropped_img = img.crop(box=(xmin, ymin, xmax, ymax))

    cropped_img.save(os.path.join('data', 'maips', '{}.jpg'.format(name)))
