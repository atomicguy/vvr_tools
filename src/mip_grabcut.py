from __future__ import division, absolute_import

import cv2
import numpy as np

from src.card import calculate_bbox, card_bbox

from PIL import Image


def gc_bounds(img):
    """Generate bounding box for grabcut"""
    # x0 = int(img.shape[1] / 10)
    # w = x0 * 8
    # y0 = int(img.shape[0] / 10)
    # h = y0 * 8
    #
    # return x0, y0, w, h
    x0, y0, x1, y1 = card_bbox(img)

    x0 = int(x0 * 1.05)
    y0 = int(y0 * 1.01)
    x1 = int(x1 * 0.95)
    y1 = int(y1 * 0.99)

    return x0, y0, x1 - x0, y1 - y0


def grabcut_estimate(img_path, scale):
    """Generate an estimated grabcut from common MIP locations"""

    img = cv2.imread(img_path)
    img = cv2.resize(img, dsize=(0, 0), fx=scale, fy=scale)
    mask = np.zeros(img.shape[:2], np.uint8)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    pil_img = Image.open(img_path)
    scaled = pil_img.resize((int(pil_img.width * scale), int(pil_img.height * scale)))

    rect = gc_bounds(scaled)

    # img_data = Image.fromarray(img)
    # x0 = rect[0]
    # y0 = rect[1]
    # x1 = x0 + rect[2]
    # y1 = y0 + rect[3]
    # cropped = img_data.crop((x0, y0, x1, y1))
    # cropped.save('data/73_gc_cards/test.jpg')
    # print(x0, y0, x1, y1)
    # exit()

    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    gc_img = img * mask2[:, :, np.newaxis]

    # Image.fromarray(gc_img).save('data/72_grabcut/test.jpg')

    return gc_img


def gc_cleanup(img, k_scale=0.05):
    """Morphologically Open the GrabCut image"""

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h = int(img.shape[0] * k_scale)
    w = int(img.shape[1] * k_scale)

    kernel = np.ones((w, h), np.uint8)

    opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    return opened


def mip_bbox(img_path, scale=0.5):
    """Calculate bounding box from cleaned grabcut'd image"""

    img = grabcut_estimate(img_path, scale)
    cleaned = gc_cleanup(img)

    mask = np.asarray(cleaned)
    mask[mask > 0] = 1
    mask = cv2.resize(mask, dsize=(0, 0), fx=1/scale, fy=1/scale)

    return calculate_bbox(mask)
