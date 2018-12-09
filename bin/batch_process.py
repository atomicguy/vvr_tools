from __future__ import division, absolute_import

import os
import glob
import json
import progressbar
import subprocess

from argparse import ArgumentParser
from src.card import StereoCard
from src.pairs import StereoPairGC


def find_filepaths(path, extension):
    return glob.glob('%s/*.%s' % (path, extension))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--img_dir', type=str, help='directory of images', required=True)
    parser.add_argument('--out', type=str, help='output directory', required=True)
    parser.add_argument('--eval', type=str, help='evaluate results', default=False)
    parser.add_argument('--truth', type=str, help='path to truth data', default='data/validation_cardinfo')
    args = parser.parse_args()

    card_info_path = os.path.join(args.out, 'info.json')
    mip_info_path = os.path.join(args.out, 'pairs.json')
    results_path = os.path.join(args.out, 'results')

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    if not os.path.exists(results_path):
        os.makedirs(results_path)

    card_info_list = []
    mip_info_list = []

    images = find_filepaths(args.img_dir, 'jpg')

    info = {'split_channel': 'cbcr',
            'binary': 'otsu',
            'filter_size': 5,
            'input_imgs': args.img_dir,
            'method_details':
                {'gc_type': 'rect',
                 'iter_count': 5,
                 'k_scale': 0.01,
                 'scale': 0.5,
                 'probable_background': [0.0, 0.0, 0.0, 0.0],
                 'probable_foreground': [0.0, 0.0, 0.0, 0.0],
                 'rect_scale': [0.05, 0.01, 0.05, 0.01],
                 'sure_foreground': [0.0, 0.0, 0.0, 0.0]
                 },
            'mip_method': 'grabcut',
            'out_dir': results_path}

    for img in progressbar.progressbar(sorted(images)):
        name = os.path.splitext(os.path.basename(img))[0]

        info['path'] = img

        card = StereoCard(info)
        img_data = card.img
        bbox = card.bbox

        card_info = {'name': name, 'bbox': bbox}
        card_info_list.append(card_info)

        method_details = info['method_details']
        method_details['card_bb'] = bbox
        method_details['path'] = info['path']

        mip = StereoPairGC(method_details)
        mip_bb_card = mip.mip_bbox()
        mip_bb = {'x0': mip_bb_card[0],
                  'y0': mip_bb_card[1],
                  'x1': mip_bb_card[2],
                  'y1': mip_bb_card[3]}

        mip_info = {'name': name, 'bbox': mip_bb}
        mip_info_list.append(mip_info)

        img_mip = mip.img.crop((mip_bb['x0'], mip_bb['y0'], mip_bb['x1'], mip_bb['y1']))
        img_mip.save(os.path.join(results_path, '{}.jpg'.format(name)))

    with open(card_info_path, 'w') as f:
        json.dump(card_info_list, f, indent=2)

    with open(mip_info_path, 'w') as f:
        json.dump(mip_info_list, f, indent=2)

    if json.loads(args.eval.lower()):
        eval_cmd = ['python3', 'bin/evaluate.py',
                    '--card_info', card_info_path,
                    '--pair_info', mip_info_path,
                    '--truth', args.truth,
                    '--out', args.out]

        subprocess.call(eval_cmd)
