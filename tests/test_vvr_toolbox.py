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
    assert np.max(v.get_lum_channel(img)) <= 100
    assert np.min(v.get_lum_channel(img)) >= 0


def test_round_up_to_odd():
    assert v.round_up_to_odd(2.4) == 3
    assert v.round_up_to_odd(1.1) == 3
    assert v.round_up_to_odd(0.1) == 1


# ensure mid section returned
def test_get_mid_section():
    test_image = skimage.data.chelsea()

    assert v.get_mid_section(test_image, 'wide').shape == (100, 451, 3)
    assert v.get_mid_section(test_image, 'tall').shape == (300, 150, 3)


# Ensure correct sums are calculated
def test_get_luma_sums():
    test_image = io.imread('./tests/data/test_wide.png')
    test_image = v.get_lum_channel(test_image)
    result_wide = 300 * np.asarray([1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1])
    result_tall = np.asarray([0,0,0,0,0,0,0,0,0])

    assert (v.get_luma_sums(test_image, 'width')  == result_wide).all()
    assert (v.get_luma_sums(test_image, 'height') == result_tall).all()


# Ensure the correct end of np array returned
def test_get_end_third():
    test_array = np.asarray([1,2,3,4,5,6,7,8,9])

    assert (v.get_end_third(test_array,0) == [1,2,3]).all()
    assert (v.get_end_third(test_array,1) == [7,8,9]).all()

    test_array = np.asarray([1,2,3,4,5,6,7,8,9,0])

    assert (v.get_end_third(test_array, 0) == [1, 2, 3]).all()
    assert (v.get_end_third(test_array, 1) == [8, 9, 0]).all()


# Test getting partial peaks
def test_get_partial_peaks():
    test_image = io.imread('./tests/data/test_wide.png')
    result_wide = np.asarray([ 300,300,300,300,300,300,300,300,300])
    result_tall = np.asarray([0,0,0])

    assert (v.get_partial_peaks(test_image, 'width', 0) == result_wide).all()
    assert len(v.get_partial_peaks(test_image, 'width', 0)) == len(result_wide)
    assert (v.get_partial_peaks(test_image, 'height', 0) == result_tall).all()


# Test getting index of peak value
def test_get_max_point():
    test_array = np.asarray([0,0,0,1,0,0])

    assert v.get_max_point(test_array) == 3


# Test get peaks
def test_get_max_peaks():
    test_image = io.imread('./tests/data/test_wide.png')

    assert v.get_max_peaks(test_image) == [0,18]