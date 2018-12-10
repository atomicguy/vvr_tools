from __future__ import division, absolute_import

from PIL import Image
from src.img_ops import single_channel, binary, filter_binary
from src.measures import calculate_bbox


class StereoCard:
    def __init__(self, config):
        self.config = config
        self.img = Image.open(config['path'])
        self.gray = single_channel(self.img, config['split_channel'])
        self.binary = binary(self.gray, config['binary'])
        self.cleaned = filter_binary(self.binary, config['filter_size'])
        self.bbox = calculate_bbox(self.cleaned)
