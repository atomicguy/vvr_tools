from __future__ import division, absolute_import

import os
import csv
import json
import subprocess

from argparse import ArgumentParser


def run_trial(trial):
    trial_cmd = ['python3', 'bin/measure_card.py',
                 '--out_dir', trial['out_dir'],
                 '--split', trial['split'],
                 '--binary', trial['binary'],
                 '--f_size', trial['f_size'],
                 '--image_dir', trial['input_imgs'],
                 '--truth', trial['truth_data']]

    subprocess.call(trial_cmd)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--configs', type=str, help='json of configs', required=True)
    parser.add_argument('--out', type=str, help='dir for output csv', required=True)
    args = parser.parse_args()

    with open(args.configs, 'r') as f:
        trials = json.load(f)

    results_csv = []

    for trial in trials:
        results = os.path.join(trial['out_dir'], 'mean_iou.txt')

        if not os.path.exists(results):
            run_trial(trial)
        else:
            with open(results, 'r') as f:
                iou = f.read()
            print('iou for {} is {}'.format(results, iou))

        with open(results, 'r') as f:
            iou = f.read()

        trial['iou'] = iou
        results_csv.append(trial)

    keys = results_csv[0].keys()
    with open(os.path.join(args.out, 'results.csv'), 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results_csv)
