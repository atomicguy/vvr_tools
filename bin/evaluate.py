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

        x0 = maip_bbox['x0']
        y0 = maip_bbox['y0']
        x1 = maip_bbox['x1']
        y1 = maip_bbox['y1']

        truth = etree.parse(os.path.join(args.truth, '{}.xml'.format(name)))
        maip = truth.xpath("//*[local-name()='object']/*[text()='MAIP']/./..")[0]
        t_xmin = int(maip.find('bndbox/xmin').text)
        t_xmax = int(maip.find('bndbox/xmax').text)
        t_ymin = int(maip.find('bndbox/ymin').text)
        t_ymax = int(maip.find('bndbox/ymax').text)

        maip_iou = bb_intersection_over_union((x0, y0, x1, y1), (t_xmin, t_ymin, t_xmax, t_ymax))

        card = truth.xpath("//*[local-name()='object']/*[text()='Card']/./..")[0]
        c_xmin = int(card.find('bndbox/xmin').text)
        c_xmax = int(card.find('bndbox/xmax').text)
        c_ymin = int(card.find('bndbox/ymin').text)
        c_ymax = int(card.find('bndbox/ymax').text)

        card_iou = bb_intersection_over_union((card_bbox[0], card_bbox[1], card_bbox[2], card_bbox[3]), 
                                              (c_xmin, c_ymin, c_xmax, c_ymax))

        ious.append({'name': name, 'maip_iou': maip_iou, 'card_iou': card_iou})

    with open(os.path.join(args.out, 'ious.json'), 'w') as f:
        json.dump(ious, f, indent=2)

    maip_results = [i['maip_iou'] for i in ious]
    mean_maip_iou = sum(maip_results) / float(len(maip_results))
    print('maip iou {}'.format(mean_maip_iou))

    card_results = [i['card_iou'] for i in ious]
    mean_card_iou = sum(card_results) / float(len(card_results))
    print('card iou {}'.format(mean_card_iou))

    open(os.path.join(args.out, 'maip {}'.format(mean_maip_iou)), 'w').close()
    open(os.path.join(args.out, 'card {}'.format(mean_card_iou)), 'w').close()
