from __future__ import division, absolute_import

import os
import glob
import json
import progressbar

from argparse import ArgumentParser
from PIL import Image
from src.pairs import get_pair_bounds


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of cards', required=True)
    parser.add_argument('--card_info', type=str, help='json info of card bboxes', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    parser.add_argument('--img_out', type=str, help='directory for card output', required=True)
    args = parser.parse_args()

    images = find_filepaths(args.img_dir, 'jpg')

    if not os.path.exists(args.img_out):
        os.makedirs(args.img_out)

    with open(args.card_info, 'r') as f:
        cards = json.load(f)

    info_list = []

    for img in progressbar.progressbar(images):
        name = os.path.splitext(os.path.basename(img))[0]

        full_img = Image.open(img)
        card_info = next(item for item in cards if item["name"] == name)
        # crop image to card
        xmin = card_info['bbox'][0]
        xmax = xmin + card_info['bbox'][2]
        ymin = card_info['bbox'][1]
        ymax = ymin + card_info['bbox'][3]
        img_data = full_img.crop((xmin, ymin, xmax, ymax))

        try:
            bbox = get_pair_bounds(img_data)

            info = {'name': name, 'bbox': bbox}
            info_list.append(info)
            cropped = img_data.crop((bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1']))
            cropped.save(os.path.join(args.img_out, '{}.jpg'.format(name)))

        except:
            print('error image {}'.format(name))

    with open(os.path.join(args.out, 'pairs.json'), 'w') as f:
        try:
            json.dump(info_list, f, indent=2)
        except TypeError:
            print(info_list)
