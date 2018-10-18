from __future__ import division, absolute_import

import os
import cv2
import numpy as np

from src.card import calculate_bbox


def grabcut_estimate(img_path):
    """Generate an estimated grabcut from common MIP locations"""

    img = cv2.imread(img_path)
    mask = np.zeros(img.shape[:2], np.uint8)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    x0 = int(img.shape[1] / 10)
    w = x0 * 8
    y0 = int(img.shape[0] / 10)
    h = y0 * 8

    rect = (x0, y0, w, h)

    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    gc_img = img * mask2[:, :, np.newaxis]

    return gc_img


def gc_cleanup(img, scale=0.05):
    """Morphologically Open the GrabCut image"""

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h = int(img.shape[0] * scale)
    w = int(img.shape[1] * scale)

    kernel = np.ones((w, h), np.uint8)

    opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    return opened


def mip_bbox(img_path):
    """Calculate bounding box from cleaned grabcut'd image"""

    img = grabcut_estimate(img_path)
    cleaned = gc_cleanup(img)

    mask = np.asarray(cleaned)
    mask[mask > 0] = 1

    return calculate_bbox(mask)
