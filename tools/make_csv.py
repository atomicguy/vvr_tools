from __future__ import division, absolute_import

import os
import glob
import json

from lxml import etree

def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))

cards = find_filepaths('/Volumes/Go/NYPL_Collection/annotations', 'xml')

info = []

for image in cards:
    name = '{}.jpg'.format(os.path.splitext(os.path.basename(image))[0])

    truth = etree.parse(image)
    
    width = int(truth.find('size/width').text)
    height = int(truth.find('size/height').text)

    maip = truth.xpath("//*[local-name()='object']/*[text()='MAIP']/./..")[0]
    m_xmin = int(maip.find('bndbox/xmin').text) / width
    m_xmax = int(maip.find('bndbox/xmax').text) / width
    m_ymin = int(maip.find('bndbox/ymin').text) / height
    m_ymax = int(maip.find('bndbox/ymax').text) / height

    info.append({'name': name, 'label': 'maip', 'xmin': m_xmin,
    			'ymin': m_ymin, 'xmax': m_xmax, 'ymax': m_ymax})
    			
    card = truth.xpath("//*[local-name()='object']/*[text()='Card']/./..")[0]
    c_xmin = int(card.find('bndbox/xmin').text) / width
    c_xmax = int(card.find('bndbox/xmax').text) / width
    c_ymin = int(card.find('bndbox/ymin').text) / height
    c_ymax = int(card.find('bndbox/ymax').text) / height
    
    info.append({'name': name, 'label': 'card', 'xmin': c_xmin,
    			'ymin': c_ymin, 'xmax': c_xmax, 'ymax': c_ymax})

with open(os.path.join('../data', 'new_gt_info.json'), 'w') as f:
        json.dump(info, f, indent=2)