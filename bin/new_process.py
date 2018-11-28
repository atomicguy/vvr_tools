from __future__ import division, absolute_import

import os
import cv2
import glob
import json
import progressbar
import subprocess

from argparse import ArgumentParser
from src.card import StereoCard
from src.pairs import StereoPair, StereoPairGC
from src.mip_grabcut import mip_bbox


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

    # tmp_path = os.path.join(args.out, 'tmp')
    # if not os.path.exists(tmp_path):
    #     os.makedirs(tmp_path)

    card_info_path = os.path.join(args.out, 'info.json')
    mip_info_path = os.path.join(args.out, 'pairs.json')

    images = find_filepaths(args.img_dir, 'jpg')

    info_list = []
    card_info_list = []
    mip_info_list = []

    for img in progressbar.progressbar(sorted(images)):
        name = os.path.splitext(os.path.basename(img))[0]

        # info = {'path': img,
        #         'mip_method': 'classical',
        #         'method_details': {
        #             'mip_channel_split': 'sat',
        #             'mip_image_features': 'fft'
        #         },
        #         'split_channel': 'cbcr',
        #         'binary': 'otsu',
        #         'filter_size': 5
        #         }

        info = {'path': img,
                'mip_method': 'grabcut',
                'method_details': {
                    'scale': 0.5,
                    'iter_count': 5,
                    'k_scale': 0.05,
                    'rect_scale': [0.02, 0.02, 0.02, 0.02],
                    'gc_type': 'rect',
                    'sure_foreground': [0.1781, 0.3087, 0.7926, 0.6522],
                    'probable_foreground': [0.1247, 0.1735, 0.8624, 0.8530],
                    'probable_background': [0.0505, 0.0440, 0.9264, 0.9702]
                },
                'split_channel': 'cbcr',
                'binary': 'otsu',
                'filter_size': 5
                }

        card = StereoCard(info)

        img_data = card.img
        bbox = card.bbox

        card_info = {'name': name, 'bbox': bbox}
        card_info_list.append(card_info)

        cropped = img_data.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
        cropped.save(os.path.join(card_path, '{}.jpg'.format(name)))

        # MIP calculation
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
            # mip_data = mip_bbox(img, card_info)
            # mip_bb = {'x0': mip_data[0], 'y0': mip_data[1],
            #                'x1': mip_data[2], 'y1': mip_data[3]}
            mip = StereoPairGC(method_details)
            mip_bb_card = mip.mip_bbox()
            mip_bb = {'x0': mip_bb_card[0],
                      'y0': mip_bb_card[1],
                      'x1': mip_bb_card[2],
                      'y1': mip_bb_card[3]}

            # tmp_img = mip.in_process()
            # cv2.imwrite(os.path.join(tmp_path, '{}.jpg'.format(name)), tmp_img)

        else:
            print('No MIP method specified')
            mip_bb = [0, 0, 0, 0]

        mip_info = {'name': name, 'bbox': mip_bb}
        mip_info_list.append(mip_info)

        img_mip = img_data.crop((mip_bb['x0'], mip_bb['y0'], mip_bb['x1'], mip_bb['y1']))
        # img_mip = mip.w_features()
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
