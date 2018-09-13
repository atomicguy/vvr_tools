from __future__ import division, absolute_import

import os
import glob
import json
import progressbar

from argparse import ArgumentParser
from lxml import etree
from src.eval import bb_intersection_over_union

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--card_info', type=str, help='json info of card bboxes', required=True)
    parser.add_argument('--pair_info', type=str, help='json info for maips', required=True)
    parser.add_argument('--truth', type=str, help='ground truth dir', required=True)
    parser.add_argument('--out', type=str, help='output of results', required=True)
    args = parser.parse_args()

    with open(args.card_info, 'r') as f:
        card_info = json.load(f)

    with open(args.pair_info, 'r') as f:
        pair_info = json.load(f)

    ious = []

    for card in progressbar.progressbar(card_info):
        name = card['name']
        card_bbox = card['bbox']

        maip = next(item for item in pair_info if item["name"] == name)
        maip_bbox = maip['bbox']

        xmin = card_bbox[0]
        ymin = card_bbox[1]

        x0 = xmin + maip_bbox['x0']
        y0 = ymin + maip_bbox['y0']
        x1 = xmin + maip_bbox['x1']
        y1 = ymin + maip_bbox['y1']

        truth = etree.parse(os.path.join(args.truth, '{}.xml'.format(name)))
        t_xmin = int(truth.find('object').find('bndbox').find('xmin').text)
        t_xmax = int(truth.find('object').find('bndbox').find('xmax').text)
        t_ymin = int(truth.find('object').find('bndbox').find('ymin').text)
        t_ymax = int(truth.find('object').find('bndbox').find('ymax').text)

        iou = bb_intersection_over_union((x0, y0, x1, y1), (t_xmin, t_ymin, t_xmax, t_ymax))

        ious.append({'name': name, 'iou': iou})

    with open(os.path.join(args.out, 'ious.json'), 'w') as f:
        json.dump(ious, f, indent=2)

    results = [i['iou'] for i in ious]
    average_iou = sum(results) / float(len(results))
    print(average_iou)

    open(os.path.join(args.out, str(average_iou)), 'w').close()
