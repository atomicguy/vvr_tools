from __future__ import division, absolute_import

import os
import glob
import json
import progressbar
import matplotlib.pyplot as plt
import numpy as np

from argparse import ArgumentParser
from PIL import Image
from src.pairs import get_diff_peaks


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of cards', required=True)
    parser.add_argument('--card_info', type=str, help='json info of card bboxes', required=True)
    parser.add_argument('--out', type=str, help='output dir', required=True)
    parser.add_argument('--img_out', type=str, help='directory for card output', default='')
    args = parser.parse_args()

    images = find_filepaths(args.img_dir, 'jpg')

    if args.img_out:
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
        xmax = card_info['bbox'][2]
        ymin = card_info['bbox'][1]
        ymax = card_info['bbox'][3]
        img_data = full_img.crop((xmin, ymin, xmax, ymax))

        smoothed_x = get_diff_peaks(img_data, 0)

        width, height = img_data.size
        smoothed_x = smoothed_x / np.max(smoothed_x) * height

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(smoothed_x)
        plt.imshow(img_data)
        plt.tick_params(axis='both', which='both', bottom=False, left=False, labelbottom=False, labelleft=False)

        fig.savefig(os.path.join(args.img_out, '{}.jpg'.format(name)))

        plt.close('all')
