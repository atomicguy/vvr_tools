from __future__ import division, absolute_import

import os
import numpy as np

from skimage import color 
from skimage.filters import threshold_otsu, threshold_minimum
from skimage.morphology import diamond
from skimage.morphology import binary_erosion


def cbcr_split(image):
    """Return combination of Cb and Cr channels"""
    ycbcr = color.rgb2ycbcr(image)

    cb = ycbcr[:, :, 1]
    cr = ycbcr[:, :, 2]
    
    combo = cr + (np.max(cb) - cb)

    return combo / np.max(combo)
    
    # lab = color.rgb2lab(image)
    # a = lab[:, :, 1]
    # b = lab[:, :, 2]

    # combo = a + b

    # return combo / np.max(combo)


def binary_version(gray_image):
    """Otsu Method binary thesholded image"""
    thresh = threshold_otsu(gray_image)
    binary = gray_image > thresh

    # block_size = 35

    # local_thresh = threshold_local(gray_image, block_size, offset=10)
    # binary = gray_image > local_thresh

    # thresh_min = threshold_minimum(gray_image)
    # binary = gray_image > thresh_min

    return binary


def cleaned_image(binary_image):
    """Use Diamond shaped binary erosion to clean up image"""
    selem = diamond(7)
    cleaned = binary_erosion(binary_image, selem)

    return cleaned


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
    width = xmax-xmin
    assert width >= 0.0
    assert width < 1.0
    
    x = xmin * mask_width
    y = ymin * mask_height
    # w = (xmax - xmin) * mask_width
    # h = (ymax - ymin) * mask_height
    x1 = xmax * mask_width
    y1 = ymax * mask_height

    return [int(x), int(y), int(x1), int(y1)]


def card_bbox(image):
    """Return bbox for card of given image"""

    gray_image = cbcr_split(image)
    binary_image = binary_version(gray_image)
    cleaned = cleaned_image(binary_image)
    bbox = calculate_bbox(cleaned)

    return bbox