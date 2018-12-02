from __future__ import division, absolute_import

import os
import csv
import json
import subprocess

from argparse import ArgumentParser


def run_trial(trial):
    trial_cmd = ['python3', 'bin/measure_mip.py',
                 '--out', trial['out_dir'],
                 '--info', trial['info'],
                 '--img_dir', trial['input_imgs'],
                 '--truth', trial['truth_data'],
                 '--save_cards', 'False',
                 '--save_mips', 'False',
                 '--skip_cards', 'True']

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
        results = os.path.join(trial['out_dir'], 'mean_mip_iou.txt')

        if not os.path.exists(results):
            if not os.path.exists(trial['out_dir']):
                os.makedirs(trial['out_dir'])

            config_path = os.path.join(trial['out_dir'], 'config.json')
            trial['info'] = config_path
            with open(config_path, 'w') as f:
                json.dump(trial, f, indent=2)
            run_trial(trial)
        else:
            with open(results, 'r') as f:
                iou = f.read()
            print('iou for {} is {}'.format(results, iou))

        with open(results, 'r') as f:
            iou = f.read()

        trial['iou'] = iou

        # clean up the dict/csv
        for key, value in trial['method_details'].items():
            trial[key] = value

        _ = trial.pop('method_details', None)
        _ = trial.pop('info', None)

        results_csv.append(trial)

    keys = results_csv[0].keys()
    with open(os.path.join(args.out, 'results_pt3.csv'), 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results_csv)
