from __future__ import division, absolute_import

import os
import numpy as np

# from PIL import Image
from skimage import color 
from scipy.stats import norm
from scipy.signal import find_peaks


def just_edge_peaks(peaks, width):
    # left value is < 30% width
    # right value is > 70% width
    x0_locs = np.round(0.3 * width)
    x1_locs = np.round(0.7 * width)

    x0_pool = peaks[peaks < x0_locs]
    x1_pool = peaks[peaks > x1_locs]
    
    return (x0_pool, x1_pool)


def best_peaks(x0_pool, x1_pool, card_width):
    # Make all combinations of potential peaks
    largest_pool = np.max([len(x0_pool), len(x1_pool)])
    combinations = np.array(np.meshgrid(x0_pool, x1_pool)).T.reshape(-1, largest_pool)
    
    # Test if center (simplified formula) is near 85% image center
    img_pair_size = (combinations[:, 1] - combinations[:, 0]) / card_width
    mid_truth = np.greater(img_pair_size, np.ones_like(img_pair_size) * 0.85)
    
    # Test if left edge strip + right edge of image pair is near full image size
    est_card_size = (combinations[:, 1] + combinations[:, 0]) / card_width
    size_truth = np.isclose(est_card_size, np.ones_like(img_pair_size), rtol=0.02)
    
    # Find pairs passing both tests
    pool_truth = np.logical_and(mid_truth, size_truth)
    num_passed = np.sum(pool_truth)
    
    if num_passed == 1:
        best_combo = combinations[pool_truth == True]
        x0 = best_combo[0][0]
        x1 = best_combo[0][1]
    else:
        x0 = np.min(x0_pool)
        x1 = np.max(x1_pool)
        
    return x0, x1


def return_x_bounds(peaks, width):
    num_peaks = len(peaks)
    
    if num_peaks < 2:
        # Failsafe, return average results
        x0 = np.round(width * 0.1)
        x1 = np.round(wdith * 0.9)
    elif num_peaks == 2:
        # Twin Peaks found
        x0 = peaks[0]
        x1 = peaks[1]
    else:
        # pare down list to get most likely right and left values  
        x0_pool, x1_pool = just_edge_peaks(peaks, width)
        x0, x1 = best_peaks(x0_pool, x1_pool, width)
        
    return x0, x1


def special_gray(image_slice):
    ycbcr = color.rgb2ycbcr(image_slice)
    
    cb_invert = 255 - ycbcr[:, :, 1]
    
    # Combine and Normalize to create gray
    return (cb_invert + ycbcr[:, :, 2]) / 510


def x_bias_curve(x_data):
    # Observed Average Curve Metrics
    x0 = {'x': 0.00418, 'mu': 0.0865, 'sigma': 0.0266}
    x1 = {'x': 0.003, 'mu': 0.9143, 'sigma': 0.025}
    
    w = x_data.size
    
    # Generate scaled bias curves
    bias_l = {'x': x0['x'] * w, 'mu': x0['mu'] * w, 'sigma': x0['sigma'] * w}
    bias_r = {'x': x1['x'] * w, 'mu': x1['mu'] * w, 'sigma': x1['sigma'] * w}
    
    l_term = bias_l['x'] * norm.pdf(range(0, w), bias_l['mu'], bias_l['sigma'])
    r_term = bias_r['x'] * norm.pdf(range(0, w), bias_r['mu'], bias_r['sigma'])
    bias_term = (l_term + r_term)

    return bias_term


def y_bias_curve(y_data):
    # Observed Average Curve Metrics
    y0 = {'y': 0.0044, 'mu': 0.0420, 'sigma': 0.0186}
    y1 = {'y': 0.0088, 'mu': 0.9447, 'sigma': 0.0179}
    
    h = y_data.size
    
    # Generate scaled bias curves
    bias_l = {'y': y0['y'] * h, 'mu': y0['mu'] * h, 'sigma': y0['sigma'] * h}
    bias_r = {'y': y1['y'] * h, 'mu': y1['mu'] * h, 'sigma': y1['sigma'] * h}
    
    l_term = bias_l['y'] * norm.pdf(range(0, h), bias_l['mu'], bias_l['sigma'])
    r_term = bias_r['y'] * norm.pdf(range(0, h), bias_r['mu'], bias_r['sigma'])
    bias_term = (l_term + r_term)

    return bias_term / np.max(bias_term)
    

def get_x_points(card_img):
    w, h = card_img.size
    w_slice = card_img.crop((0, np.round(h * 1/3), w, np.round(h * 2/3)))
    gray_w = special_gray(w_slice)
    
    # Make graph of brightnesses
    intensities_w = np.squeeze(np.dot(gray_w.T, np.ones((gray_w.shape[0], 1))))
    
    # Bias the curve
    bias_term = x_bias_curve(intensities_w)
    biased_w = bias_term * intensities_w
    
    # Get peaks
    peaks = find_peaks(biased_w)[0]
    
    x0, x1 = return_x_bounds(peaks, w)
    
    return x0, x1


def return_y_bounds(peaks, biased_h, height):
    y0_pool, y1_pool = just_edge_peaks(peaks, height)
    
    if len(y0_pool) == 0:
        # Failsafe Value
        y0 = np.round(0.1 * height)
    elif len(y0_pool) == 1:
        y0 = y0_pool[0]
    else:
        # Choose Max peak values
        peak_vals = [biased_h[i] for i in y0_pool]
        idx = np.argmax(peak_vals)
        y0 = y0_pool[idx]
        
    if len(y1_pool) == 0:
        # Failsafe Value
        y1 = np.round(0.9 * height)
    elif len(y1_pool) == 1:
        y1 = y1_pool[0]
    else:
        # Choose Max peak values
        peak_vals = [biased_h[i] for i in y1_pool]
        idx = np.argmax(peak_vals)
        y1 = y1_pool[idx]
    
    return y0, y1


def get_y_points(card_img):
    w, h = card_img.size
    h_slice = card_img.crop((np.round(w * 1/3), 0, np.round(w * 2/3), h))
    gray_h = special_gray(h_slice)
    
    # Make graph of brightnesses
    intensities_h = np.squeeze(np.dot(gray_h, np.ones((gray_h.shape[1], 1))))
    
    # Bias the curve
    bias_term = y_bias_curve(intensities_h)
    biased_h = bias_term * intensities_h
    
    # Get peaks
    peaks = find_peaks(biased_h)[0]
    
    return return_y_bounds(peaks, biased_h, h)
    

def get_pair_bounds(card_img):
    x0, x1 = get_x_points(card_img)
    y0, y1 = get_y_points(card_img)
    
    return {'x0': int(x0), 'x1': int(x1), 'y0': int(y0), 'y1': int(y1)}