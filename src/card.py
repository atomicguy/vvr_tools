from __future__ import division, absolute_import

import os
import numpy as np

from PIL import Image
from skimage import color, exposure
from skimage.filters import threshold_otsu, threshold_minimum, threshold_mean, threshold_local
from skimage.morphology import binary_erosion, diamond


def calculate_bbox(mask):
    histogram_y = np.squeeze(np.dot(mask, np.ones((mask.shape[1], 1))))
    histogram_x = np.squeeze(np.dot(mask.T, np.ones((mask.shape[0], 1))))

    nonzero_y_indexes = np.squeeze(np.where(histogram_y > 0))
    nonzero_x_indexes = np.squeeze(np.where(histogram_x > 0))

    assert len(nonzero_y_indexes) > 0 and len(nonzero_x_indexes) > 0, 'mask should not be empty'

    mask_height, mask_width = mask.shape
    ymin = float(nonzero_y_indexes[0]) / mask_height
    ymax = float(nonzero_y_indexes[-1]) / mask_height
    xmin = float(nonzero_x_indexes[0]) / mask_width
    xmax = float(nonzero_x_indexes[-1]) / mask_width

    # make sure sane bbox values
    assert ymin >= 0.0
    assert ymin < 1.0
    assert ymax >= 0.0
    assert ymax < 1.0
    assert xmin >= 0.0
    assert xmin < 1.0
    assert xmax >= 0.0
    assert xmax < 1.0
    height = ymax - ymin
    assert height >= 0.0
    assert height < 1.0
    width = xmax - xmin
    assert width >= 0.0
    assert width < 1.0

    x = xmin * mask_width
    y = ymin * mask_height
    x1 = xmax * mask_width
    y1 = ymax * mask_height

    return [int(x), int(y), int(x1), int(y1)]


def single_channel(img, config):
    """Convert image to single channel

    :param img: PIL image
    :param config: dict of config information
    :return: single channel iamge
    """
    method = config['split_channel']
    img = np.asarray(img)

    if method == 'cb':
        ycbcr = color.rgb2ycbcr(img)
        gray = ycbcr[:, :, 1]

    elif method == 'cbcr':
        ycbcr = color.rgb2ycbcr(img)
        cb = ycbcr[:, :, 1]
        cr = ycbcr[:, :, 2]
        gray = cr + (np.max(cb) - cb)

    elif method == 'sat':
        hsv = color.rgb2hsv(img)
        gray = hsv[:, :, 1]

    else:
        hsv = color.rgb2hsv(img)
        gray = hsv[:, :, 2]

    return gray


def binary(img, config):
    """Threshold image

    :param img: grayscale image
    :param config: dict of config info
    :return: binary image
    """
    method = config['binary']

    if method == 'otsu':
        thresh = threshold_otsu(img)
        binary = img > thresh

    elif method == 'mean':
        thresh = threshold_mean(img)
        binary = img > thresh
        binary = 1 - binary

    elif method == 'local':
        thresh = threshold_local(img, 35, offset=10)
        binary = img > thresh

    else:
        thresh = threshold_minimum(img)
        binary = img > thresh

    return binary


def filter_binary(img, config):
    size = config['filter_size']

    selem = diamond(size)
    cleaned = binary_erosion(img, selem)

    return cleaned


class StereoCard:
    def __init__(self, config):
        self.config = config
        self.img = Image.open(config['path'])
        self.gray = single_channel(self.img, self.config)
        self.binary = binary(self.gray, self.config)
        self.cleaned = filter_binary(self.binary, self.config)
        self.bbox = calculate_bbox(self.cleaned)


def cbcr_split(image):
    """Return combination of Cb and Cr channels"""
    ycbcr = color.rgb2ycbcr(image)

    cb = ycbcr[:, :, 1]
    # cr = ycbcr[:, :, 2]
    #
    # combo = cr + (np.max(cb) - cb)
    #
    # return exposure.equalize_adapthist(combo / np.max(combo), clip_limit=0.03)
    
    # lab = color.rgb2lab(image)
    # a = lab[:, :, 1]
    # b = lab[:, :, 2]

    # combo = a + b

    # return combo / np.max(combo)

    # hsv = color.rgb2hsv(image)
    # sat = hsv[:, :, 1]
    #
    # return sat
    #
    # return exposure.equalize_hist(sat / np.max(sat))

    # grey = color.rgb2luv(image)[:, :, 0]
    # return grey

    # yuv = color.rgb2yuv(image)
    # v = yuv[:, :, 2]
    # img_eq = exposure.equalize_adapthist(v, clip_limit=0.03)
    # return img_eq

    return cb


def binary_version(gray_image):
    """Otsu Method binary thesholded image"""
    # thresh = threshold_otsu(gray_image)
    # binary = gray_image > thresh

    # block_size = 35

    # local_thresh = threshold_local(gray_image, block_size, offset=10)
    # binary = gray_image > local_thresh

    # thresh_min = threshold_minimum(gray_image)
    # binary = gray_image > thresh_min

    thresh_mean = threshold_mean(gray_image)
    binary = gray_image > thresh_mean
    binary = 1 - binary

    return binary


def cleaned_image(binary_image):
    """Use Diamond shaped binary erosion to clean up image"""
    selem = diamond(7)
    cleaned = binary_erosion(binary_image, selem)

    return cleaned


def card_bbox(image):
    """Return bbox for card of given image"""

    gray_image = cbcr_split(image)
    binary_image = binary_version(gray_image)
    cleaned = cleaned_image(binary_image)
    bbox = calculate_bbox(cleaned)

    return bbox
