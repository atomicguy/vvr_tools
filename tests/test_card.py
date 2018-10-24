from __future__ import division, absolute_import
import src.card as card
import pytest
import numpy as np


# Test bounding box calculation
def test_calculate_bbox():
    mask = np.zeros((5, 7))
    mask[2:4, 3:6] = 1

    x0, y0, x1, y1 = card.calculate_bbox(mask)

    assert x0 == 3
    assert y0 == 2
    assert x1 == 5
    assert y1 == 3