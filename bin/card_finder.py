from __future__ import division, absolute_import

import os
import glob
import json
import progressbar

from argparse import ArgumentParser
from src.card import StereoCard


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of images', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    parser.add_argument('--split', type=str, help='method used for grayscale', required=True)
    parser.add_argument('--binary', type=str, help='binary threshold method', required=True)
    parser.add_argument('--filter_size', type=str, help='size of filter', required=True)
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    card_path = os.path.join(args.out, 'cards')
    if not os.path.exists(card_path):
        os.makedirs(card_path)

    images = find_filepaths(args.img_dir, 'jpg')

    info_list = []

    for img in progressbar.progressbar(images):
        name = os.path.splitext(os.path.basename(img))[0]

        info = {'path': img,
                'split_channel': args.split,
                'binary': args.binary,
                'filter_size': int(args.filter_size)}

        card = StereoCard(info)

        img_data = card.img
        bbox = card.bbox

        info = {'name': name, 'bbox': bbox}
        info_list.append(info)

        cropped = img_data.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
        cropped.save(os.path.join(card_path, '{}.jpg'.format(name)))

    with open(os.path.join(args.out, 'info.json'), 'w') as f:
        json.dump(info_list, f, indent=2)
