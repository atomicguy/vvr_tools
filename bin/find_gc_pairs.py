from __future__ import division, absolute_import

import os
import glob
import json
import progressbar
import subprocess

from argparse import ArgumentParser
from PIL import Image
from src.mip_grabcut import mip_bbox


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of cards', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    parser.add_argument('--card_info', type=str, help='json of card info',
                        default='data/gt_card_info.json')
    parser.add_argument('--truth', type=str, help='directory of groundtruth data',
                        default='data/validation_cardinfo')
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    images = find_filepaths(args.img_dir, 'jpg')

    img_out = os.path.join(args.out, 'maips')
    if not os.path.exists(img_out):
        os.makedirs(img_out)

    info_list = []

    for img in progressbar.progressbar(images):
        name = os.path.splitext(os.path.basename(img))[0]

        raw_bbox = mip_bbox(img)
        x0, y0, x1, y1 = raw_bbox
        bbox = {'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}

        full_img = Image.open(img)

        info = {'name': name, 'bbox': bbox}
        info_list.append(info)
        cropped = full_img.crop((bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1']))
        cropped.save(os.path.join(img_out, '{}.jpg'.format(name)))

    pair_info_path = os.path.join(args.out, 'pairs.json')

    with open(pair_info_path, 'w') as f:
        try:
            json.dump(info_list, f, indent=2)
        except TypeError:
            print(info_list)

    eval_cmd = ['python3', 'bin/evaluate.py',
                '--card_info', args.card_info,
                '--pair_info', pair_info_path,
                '--truth', args.truth,
                '--out', args.out]

    subprocess.call(eval_cmd)
