from __future__ import division, absolute_import

import os
import cv2
import glob
import json
import progressbar
import subprocess

from argparse import ArgumentParser
from shutil import copyfile

from src.card import StereoCard
from src.pairs import StereoPair, StereoPairGC


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))

def ready_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of images', required=True)
    parser.add_argument('--truth', type=str, help='ground truth dir', required=True)
    parser.add_argument('--info', type=str, help='path to json dict of settings', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    parser.add_argument('--save_cards', type=str, help='save card images', default=False)
    parser.add_argument('--save_mips', type=str, help='save mip images', default=False)
    parser.add_argument('--skip_cards', type=str, help='skip card calc step', default=False)
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    card_path = os.path.join(args.out, 'cards')
    mip_path = os.path.join(args.out, 'mip')

    # Uncomment if step images are needed
    # tmp_path = os.path.join(args.out, 'tmp')
    # if not os.path.exists(tmp_path):
    #     os.makedirs(tmp_path)

    card_info_path = os.path.join(args.out, 'info.json')
    mip_info_path = os.path.join(args.out, 'pairs.json')

    # If skipping card calculation, copy the card data
    if json.loads(args.skip_cards.lower()):
        copyfile('./data/truth_info.json', card_info_path)
        with open(card_info_path, 'r') as f:
            card_data = json.load(f)

    images = find_filepaths(args.img_dir, 'jpg')

    info_list = []
    card_info_list = []
    mip_info_list = []

    for img in progressbar.progressbar(sorted(images)):
        name = os.path.splitext(os.path.basename(img))[0]

        with open(args.info, 'r') as f:
            info = json.load(f)

        info['path'] = img

        if json.loads(args.skip_cards.lower()):
            card_info = next(item for item in card_data if item['name'] == name)
            bbox = card_info['bbox']

        else:
            # Find stereo card
            card = StereoCard(info)

            img_data = card.img
            bbox = card.bbox

        card_info = {'name': name, 'bbox': bbox}
        card_info_list.append(card_info)

        if json.loads(args.save_cards.lower()):
            ready_dir(card_path)
            cropped = img_data.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            cropped.save(os.path.join(card_path, '{}.jpg'.format(name)))

        # Find MIP
        method_details = info['method_details']
        method_details['card_bb'] = bbox
        method_details['path'] = info['path']

        if info['mip_method'] == 'classical':
            mip = StereoPair(method_details)
            mip_bb_card = mip.mip_bbox()
            xmin = bbox[0]
            ymin = bbox[1]
            mip_bb = {'x0': xmin + mip_bb_card['x0'],
                      'x1': xmin + mip_bb_card['x1'],
                      'y0': ymin + mip_bb_card['y0'],
                      'y1': ymin + mip_bb_card['y1']}

        elif info['mip_method'] == 'grabcut':
            mip = StereoPairGC(method_details)
            mip_bb_card = mip.mip_bbox()
            mip_bb = {'x0': mip_bb_card[0],
                      'y0': mip_bb_card[1],
                      'x1': mip_bb_card[2],
                      'y1': mip_bb_card[3]}

            # Uncomment if a saved image with grabcut rect drawn is desired
            # tmp_img = mip.in_process()
            # cv2.imwrite(os.path.join(tmp_path, '{}.jpg'.format(name)), tmp_img)

        else:
            print('No MIP method specified')
            mip_bb = [0, 0, 0, 0]

        mip_info = {'name': name, 'bbox': mip_bb}
        mip_info_list.append(mip_info)

        if json.loads(args.save_mips.lower()):
            ready_dir(mip_path)
            img_data = mip.img
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
