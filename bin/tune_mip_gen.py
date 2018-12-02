import os
import json

image_dir = 'data/validation_set'
truth = 'data/validation_cardinfo'

out_base = 'data/tune_only_mip_det'

mip_splits = ['cb', 'cr', 'cbcr', 'sat', 'val']
mip_features = ['fft', 'hog', 'sobel', 'none']

# i = 0
# trials = []
# for mip_split in mip_splits:
#     for mip_feature in mip_features:
#         out_dir = os.path.join(out_base, str(i).zfill(4))
#         trial = {'out_dir': out_dir,
#                  'split': 'none',
#                  'binary': 'none',
#                  'f_size': 1,
#                  'input_imgs': image_dir,
#                  'truth_data': truth,
#                  'mip_method': 'classical',
#                  'method_details':
#                      {'mip_channel_split': mip_split,
#                       'mip_image_features': mip_feature}
#                  }
#         trials.append(trial)
#         i += 1
#
# with open('data/tune_only_mip_det.json', 'w') as f:
#     json.dump(trials, f, indent=2)

# iter_counts = [3, 5]
# scales = [0.1, 0.5]
# k_scales = [0.01, 0.05, 0.10]
# rect_scales = [[0.01, 0.01, 0.01, 0.01],
#                [0.02, 0.01, 0.02, 0.01],
#                [0.02, 0.02, 0.02, 0.02],
#                [0.01, 0.02, 0.01, 0.02],
#                [0.05, 0.02, 0.05, 0.02],
#                [0.05, 0.05, 0.05, 0.05],
#                [0.02, 0.05, 0.02, 0.05],
#                [0.05, 0.05, 0.05, 0.05],
#                [0.01, 0.05, 0.01, 0.05],
#                [0.05, 0.01, 0.05, 0.01]]
#
#
# i = 20

# iter_counts = [5]
# scales = [0.1, 0.25, 0.5]
# k_scales = [0.01, 0.05, 0.10]
# rect_scales = [[0.05, 0.05, 0.01, 0.01],
#                [0.05, 0.01, 0.01, 0.05],
#                [0.05, 0.03, 0.05, 0.03],
#                [0.01, 0.05, 0.05, 0.01]]
#
#
# i = 140
#
# trials = []
# for iter_count in iter_counts:
#     for scale in scales:
#         for k_scale in k_scales:
#             for rect_scale in rect_scales:
#                 out_dir = os.path.join(out_base, str(i).zfill(4))
#                 trial = {'out_dir': out_dir,
#                          'split': 'none',
#                          'binary': 'none',
#                          'f_size': 1,
#                          'input_imgs': image_dir,
#                          'truth_data': truth,
#                          'mip_method': 'grabcut',
#                          'method_details':
#                              {'gc_type': 'rect',
#                               'probable_background': [0.0, 0.0, 0.0, 0.0],
#                               'probable_foreground': [0.0, 0.0, 0.0, 0.0],
#                               'sure_foreground': [0.0, 0.0, 0.0, 0.0],
#                               'iter_count': iter_count,
#                               'scale': scale,
#                               'k_scale': k_scale,
#                               'rect_scale': rect_scale}
#                          }
#                 trials.append(trial)
#                 i += 1
#
# with open('data/tune_only_mip_det_pt3.json', 'w') as f:
#     json.dump(trials, f, indent=2)

iter_counts = [5]
scales = [0.1, 0.25, 0.5]
k_scales = [0.01, 0.05, 0.10]
rect_scales = [[0.05, 0.05, 0.01, 0.01],
               [0.05, 0.01, 0.01, 0.05],
               [0.05, 0.03, 0.05, 0.03],
               [0.01, 0.05, 0.05, 0.01]]


i = 176

trials = []
for iter_count in iter_counts:
    for scale in scales:
        for k_scale in k_scales:
            for rect_scale in rect_scales:
                out_dir = os.path.join(out_base, str(i).zfill(4))
                trial = {'out_dir': out_dir,
                         'split': 'none',
                         'binary': 'none',
                         'f_size': 1,
                         'input_imgs': image_dir,
                         'truth_data': truth,
                         'mip_method': 'grabcut',
                         'method_details':
                             {'gc_type': 'rect',
                              'probable_background': [0.0, 0.0, 0.0, 0.0],
                              'probable_foreground': [0.0, 0.0, 0.0, 0.0],
                              'sure_foreground': [0.0, 0.0, 0.0, 0.0],
                              'iter_count': iter_count,
                              'scale': scale,
                              'k_scale': k_scale,
                              'rect_scale': rect_scale}
                         }
                trials.append(trial)
                i += 1

with open('data/tune_only_mip_det_pt3.json', 'w') as f:
    json.dump(trials, f, indent=2)