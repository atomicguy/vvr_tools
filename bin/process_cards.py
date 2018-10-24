from __future__ import division, absolute_import

import os
import glob
import subprocess

from argparse import ArgumentParser


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

    card_info = os.path.join(args.out, 'info.json')
    maip_info = 'data/truth_pairs.json'
    # maip_info = os.path.join(args.out, 'pairs.json')
    # maip_dir = os.path.join(args.out, 'maips')

    print('Finding Card Bounds')
    if not os.path.exists(card_info):
        card_cmd = ['python3', 'bin/find_cards.py', 
                    '--img_dir', args.img_dir,
                    '--out', args.out]
        
        subprocess.call(card_cmd)
    else:
        print('Card info already calculated')

    # print('Finding MAIPs')
    # if not os.path.exists(maip_info):
    #     maip_cmd = ['python3', 'bin/find_pairs.py',
    #                 '--img_dir', args.img_dir,
    #                 '--card_info', card_info,
    #                 '--out', args.out,
    #                 '--img_out', maip_dir]
    #
    #     subprocess.call(maip_cmd)
    # else:
    #     print('Pair maip info already calculated')

    print('Evaluating')
    eval_cmd = ['python3', 'bin/evaluate.py', 
           '--card_info', card_info, 
           '--pair_info', maip_info,
           '--truth', args.truth, 
           '--out', args.out]

    subprocess.call(eval_cmd)
