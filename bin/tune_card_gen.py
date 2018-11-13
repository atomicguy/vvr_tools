import os
import json

image_dir = 'data/validation_set'
truth = 'data/validation_cardinfo'

out_base = 'data/tune_card_det'

splits = ['cb', 'cr', 'cbcr', 'sat', 'val']
binaries = ['mean', 'local', 'otsu', 'min']
f_sizes = ['3', '5', '7', '9', '11']

trials = []
i = 0

for split in splits:
    for binary in binaries:
        for f_size in f_sizes:
            out_dir = os.path.join(out_base, str(i).zfill(3))
            trial = {'out_dir': out_dir,
                     'split': split,
                     'binary': binary,
                     'f_size': f_size,
                     'input_imgs': image_dir,
                     'truth_data': truth}
            trials.append(trial)
            i = i + 1

with open('tuning_study.json', 'w') as f:
    json.dump(trials, f, indent=2)