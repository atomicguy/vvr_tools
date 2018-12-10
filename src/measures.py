from __future__ import division, absolute_import

import numpy as np


def bb_intersection_over_union(boxA, boxB):
    """Calculate Intersection Over Union"""
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


def calculate_bbox(mask):
    """Calculate Bounding Box of white pixels in binary image"""
    histogram_y = np.squeeze(np.dot(mask, np.ones((mask.shape[1], 1))))
    histogram_x = np.squeeze(np.dot(mask.T, np.ones((mask.shape[0], 1))))

    nonzero_y_indexes = np.squeeze(np.where(histogram_y > 0))
    nonzero_x_indexes = np.squeeze(np.where(histogram_x > 0))

    assert len(nonzero_y_indexes) > 0 and len(nonzero_x_indexes) > 0, 'mask should not be empty'
    # if len(nonzero_y_indexes) >= 0 and len(nonzero_x_indexes) >= 0:
    #     return [0, 0, 0, 0]

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

    x0 = xmin * mask_width
    y0 = ymin * mask_height
    x1 = xmax * mask_width
    y1 = ymax * mask_height

    return [int(x0), int(y0), int(x1), int(y1)]
