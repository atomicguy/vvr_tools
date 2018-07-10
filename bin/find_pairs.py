from __future__ import division, absolute_import

import os
import glob
import json

from argparse import ArgumentParser
from PIL import Image
from src.pairs import get_pair_bounds


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of cards', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    args = parser.parse_args()

    images = find_filepaths(args.img_dir, 'jpg')

    info_list = []

    for img in images:
        name = os.path.splitext(os.path.basename(img))[0]

        img_data = Image.open(img)

        try:
            bbox = get_pair_bounds(img_data)

            info = {'name': name, 'bbox': bbox}
            info_list.append(info)
        except:
            print('error image {}'.format(name))

    with open(os.path.join(args.out, 'pairs.json'), 'w') as f:
        try:
            json.dump(info_list, f, indent=2)
        except TypeError:
            print(info_list)
