from __future__ import division, absolute_import

import os
import glob
import json
import progressbar
import subprocess

from argparse import ArgumentParser
from src.card import StereoCard
from src.pairs import StereoPair


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of images', required=True)
    parser.add_argument('--truth', type=str, help='ground truth dir', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    card_path = os.path.join(args.out, 'cards')
    if not os.path.exists(card_path):
        os.makedirs(card_path)

    mip_path = os.path.join(args.out, 'mip')
    if not os.path.exists(mip_path):
        os.makedirs(mip_path)

    card_info_path = os.path.join(args.out, 'info.json')
    mip_info_path = os.path.join(args.out, 'pairs.json')

    images = find_filepaths(args.img_dir, 'jpg')

    info_list = []
    card_info_list = []
    mip_info_list = []

    for img in progressbar.progressbar(images):
        name = os.path.splitext(os.path.basename(img))[0]

        info = {'path': img,
                'split_channel': 'cbcr',
                'binary': 'otsu',
                'filter_size': 5}

        card = StereoCard(info)

        img_data = card.img
        bbox = card.bbox

        card_info = {'name': name, 'bbox': bbox}
        card_info_list.append(card_info)
        info['card_bb'] = bbox

        cropped = img_data.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
        cropped.save(os.path.join(card_path, '{}.jpg'.format(name)))

        # MIP calculation
        mip = StereoPair(info)
        mip_bb_card = mip.mip_bb()

        xmin = bbox[0]
        ymin = bbox[1]
        mip_bb = {'x0': xmin + mip_bb_card['x0'],
                  'x1': xmin + mip_bb_card['x1'],
                  'y0': ymin + mip_bb_card['y0'],
                  'y1': ymin + mip_bb_card['y1']}

        mip_info = {'name': name, 'bbox': mip_bb}
        mip_info_list.append(mip_info)

        img_mip = img_data.crop((mip_bb['x0'], mip_bb['y0'], mip_bb['x1'], mip_bb['y1']))
        img_mip.save(os.path.join(mip_path, '{}.jpg'.format(name)))

    with open(card_info_path, 'w') as f:
        json.dump(card_info_list, f, indent=2)

    with open(mip_info_path, 'w') as f:
        json.dump(mip_info_list, f, indent=2)

    print('Evaluating')
    eval_cmd = ['python3', 'bin/evaluate.py',
                '--card_info', card_info_path,
                '--pair_info', mip_info_path,
                '--truth', args.truth,
                '--out', args.out]

    subprocess.call(eval_cmd)
