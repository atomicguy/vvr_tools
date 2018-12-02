from __future__ import division, absolute_import

import os
import glob
import json
import progressbar
import subprocess

from argparse import ArgumentParser
from lxml import etree
from src.measures import bb_intersection_over_union


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    # parser.add_argument('--config', type=str, help='dictionary of config info', required=True)
    parser.add_argument('--out_dir', type=str, help='out directory', required=True)
    parser.add_argument('--split', type=str, help='channel split method', required=True)
    parser.add_argument('--binary', type=str, help='threshold method', required=True)
    parser.add_argument('--f_size', type=str, help='filter size', required=True)
    parser.add_argument('--image_dir', type=str, help='directory of images to process', required=True)
    parser.add_argument('--truth', type=str, help='truth dir', required=True)
    args = parser.parse_args()

    out_dir = args.out_dir
    split = args.split
    binary = args.binary
    f_size = args.f_size
    truth = args.truth
    img_dir = args.image_dir

    # set up output locations
    card_out = os.path.join(out_dir, 'info.json')

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)


    print('Finding Card Bounds')
    card_cmd = ['python3', 'bin/card_finder.py',
                '--img_dir', img_dir,
                '--out', out_dir,
                '--split', split,
                '--binary', binary,
                '--filter_size', f_size]
        
    subprocess.call(card_cmd)

    print('Evaluating')
    with open(card_out, 'r') as f:
        card_info = json.load(f)

    ious = []

    for card in progressbar.progressbar(card_info):
        name = card['name']
        card_bbox = card['bbox']

        truth = etree.parse(os.path.join(args.truth, '{}.xml'.format(name)))

        card = truth.xpath("//*[local-name()='object']/*[text()='Card']/./..")[0]
        c_xmin = int(card.find('bndbox/xmin').text)
        c_xmax = int(card.find('bndbox/xmax').text)
        c_ymin = int(card.find('bndbox/ymin').text)
        c_ymax = int(card.find('bndbox/ymax').text)

        card_iou = bb_intersection_over_union((card_bbox[0], card_bbox[1], card_bbox[2], card_bbox[3]),
                                              (c_xmin, c_ymin, c_xmax, c_ymax))

        ious.append({'name': name, 'card_iou': card_iou})

    card_results = [i['card_iou'] for i in ious]
    mean_card_iou = sum(card_results) / float(len(card_results))
    print('card iou {}'.format(mean_card_iou))

    open(os.path.join(args.out_dir, 'card {}'.format(mean_card_iou)), 'w').close()

    with open(os.path.join(args.out_dir, 'mean_iou.txt'), 'w') as f:
        f.write(str(mean_card_iou))

