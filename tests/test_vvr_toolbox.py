from __future__ import division, absolute_import
import src.vvr_toolbox as v
import pytest
import skimage
from skimage import data, io, filters, color, img_as_float
import numpy as np


# Ensure a get list of images
def test_get_list_of_images():
    assert type(v.get_list_of_images('./FL/')) == list
    assert len(v.get_list_of_images('./FL/')) == 1345


def test_get_lum_channel():
    img = skimage.data.imread('./FL/G90F121_001F.jpg')

    assert type(v.get_lum_channel(img)) == type(img)


def test_round_up_to_odd():
    assert v.round_up_to_odd(2.4) == 3
    assert v.round_up_to_odd(1.1) == 3
    assert v.round_up_to_odd(0.1) == 1


# # try out signal smoothing
# def test_smooth_values():
#     test_array = np.array([0,1,0,1,0,1])
#
#     assert v.smooth_values(test_array) == [0,0.5,0,0.5,0,0.5]


# test finding edge points
def test_get_edge_point():
    test_array = np.array([0,1,0,0,0,0,0,0,1,0])

    assert v.get_edge_point(test_array, 0) == 1
    assert v.get_edge_point(test_array, 1) == 2
