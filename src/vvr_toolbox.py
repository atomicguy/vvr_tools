#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 16:11:24 2017

@author: atom
"""

from __future__ import division, absolute_import
import os
import skimage
from skimage import io
from skimage import color
import numpy as np
from scipy import signal
import scipy.signal.signaltools as sigtool


# get list of images
def get_list_of_images(image_dir):
    list_of_images = []
    for file in os.listdir(image_dir):
        if file.endswith('.jpg'):
            list_of_images.append(file)

    return list_of_images


# get the luminance channel of image
def get_lum_channel(sk_image):
    image_lab = skimage.color.rgb2lab(sk_image)
    image_l = skimage.color.rgb2gray(image_lab[:, :, 0])

    return image_l


# get the middle 3rd of the image in x or y
def get_mid_section(sk_image, direction):
    img_size = sk_image.shape
    # size_third = int(np.floor(img_size/3))
    if direction == 'wide':
        img_height = int(np.floor(img_size[0]/3))
        middle_section = sk_image[img_height:(2*img_height), :]
    elif direction == 'tall':
        img_width = int(np.floor(img_size[1]/3))
        middle_section = sk_image[:, img_width:(2*img_width)]
    else:
        print('include width or height as direction')

    return middle_section


# generate graph of brightness in x or y
def get_luma_sums(luma_image, direction):
    if direction == 'width':
        middle_section = get_mid_section(luma_image, 'wide')
        direction_id = 0
    elif direction == 'height':
        middle_section = get_mid_section(luma_image, 'tall')
        direction_id = 1
    else:
        print('include direction for summation')
    summation = np.sum(middle_section, axis=direction_id)

    return summation


# round up to nearest odd number
def round_up_to_odd(f):
    f = int(np.ceil(f))
    return f + 1 if f % 2 == 0 else f


# get first or last third of values
def get_end_third(luma_peaks, end):
    length = len(luma_peaks)
    one_third = int(np.floor(length/3))
    if end == 0:
        third = luma_peaks[0:one_third]
    elif end == 1:
        third = luma_peaks[-one_third:]
    else:
        print('end value must be 0 or 1')

    return third


# filter luminance channel sum
def smooth_values(sum_of_luma):
    window_length = round_up_to_odd(sum_of_luma.shape[0] / 100)
    x_filtered = signal.savgol_filter(sum_of_luma, window_length, 0)

    return x_filtered


def get_partial_peaks(image, direction, part):
    """
    Return the summed luma for specified portion of image
    :param image: scikit image to be processed
    :param direction: are we calculating (width or height)
    :param part: the start or end of a section (0 or 1)
    :return: a nparray of summed luma values
    """
    image_luma = get_lum_channel(image)
    luma_sums = get_luma_sums(image_luma, direction)
    smooth_luma_sums = smooth_values(luma_sums)
    part_sums = get_end_third(smooth_luma_sums, part)

    return part_sums


# find max value in array
def get_max_point(array_of_values):
    index = np.argmax(array_of_values)

    return index


# get max peaks
def get_max_peaks(image):
    # get peaks across width of image
    left_part = get_partial_peaks(image, 'width', 0)
    left_idx = get_max_point(left_part)

    right_part = get_partial_peaks(image, 'width', 1)
    length = image.shape[1]
    two_thirds = int(np.floor(length/3)) * 2
    right_pt_idx = get_max_point(right_part)
    right_idx = right_pt_idx + two_thirds

    lr_points = [left_idx, right_idx]
    return lr_points


# square wave of luminance channel sum
def make_luma_binary(luma_image, direction):
    sum_of_luma = get_luma_sums(luma_image, direction)
    smoothed_values = smooth_values(sum_of_luma)
    env = np.abs(sigtool.hilbert(smoothed_values))
    threshold = np.mean(smoothed_values)
    square_sig = (env > threshold)

    return square_sig


def get_edge_point(square_wave, direction):
    """
    Find the edge values for cropping on one side of the image
    :param square_wave: square wave from sum of luma channel
    :param direction: 0 for from left, 1 for from right
    :return: edge point value
    """
    length = len(square_wave)
    length_third = int(np.floor(length/3))
    if direction == 0:
        search_array = square_wave[0:length_third]
        indices = np.nonzero(search_array)
        edge = np.max(indices)
    if direction == 1:
        search_array = square_wave[2*length_third:-1]
        indices = np.nonzero(search_array)
        edge = np.min(indices) + 2*length_third

    return edge


# get edges of card
def get_bndbox(image):
    """
    Cacluate the bounding box for the right/left pair in a stereocard
    :param image: scikit-image image
    :return: [xmin, xmax, ymin, ymax]
    """
    img_luma = get_lum_channel(image)

    # for x direction
    x_sums = get_luma_sums(img_luma, 'width')
    x_binary = make_luma_binary(x_sums)
    xmin = get_edge_point(x_binary, 0)
    xmax = get_edge_point(x_binary, 1)

    # for y direction
    y_sums = get_luma_sums(img_luma, 'height')
    y_binary = make_luma_binary(y_sums)
    ymin = get_edge_point(y_binary, 0)
    ymax = get_edge_point(y_binary, 1)

    bndbox =  [xmin, xmax, ymin, ymax]

    print('bbox is', bndbox)
    return bndbox
