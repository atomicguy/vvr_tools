from __future__ import division, absolute_import

import os
import cv2
import numpy as np

from PIL import Image
from skimage import color
from skimage.feature import hog
from skimage.filters import sobel_v
from scipy.stats import norm
from scipy.signal import find_peaks, medfilt, lfilter

from src.img_ops import single_channel, binary, filter_binary, fft_filter
from src.measures import calculate_bbox


class StereoPairGC:
    def __init__(self, config):
        self.config = config
        self.scale = config['scale']
        self.img = Image.open(config['path'])
        self.card_bb = config['card_bb']
        self.cv_img = cv2.imread(config['path'])
        self.scaled = cv2.resize(self.cv_img, dsize=(0, 0), fx=self.scale, fy=self.scale)

    def gc_mask(self):
        h, w = self.scaled.shape[:2]
        fg = (np.asarray([w, h, w, h]) * self.config['sure_foreground']).astype(int)
        pfg = (np.asarray([w, h, w, h]) * self.config['probable_foreground']).astype(int)
        pbg = (np.asarray([w, h, w, h]) * self.config['probable_background']).astype(int)

        mask = np.zeros(self.scaled.shape[:2], np.uint8)
        mask[pbg[1]:pbg[3], pbg[0]:pbg[2]] = 3
        mask[pfg[1]:pfg[3], pfg[0]:pfg[2]] = 2
        mask[fg[1]:fg[3], fg[0]:fg[2]] = 1

        return mask

    def rect(self):
        h, w = self.scaled.shape[:2]
        x0, y0, x1, y1 = np.asarray(self.card_bb) * self.scale
        x0_, y0_, x1_, y1_ = self.config['rect_scale']
        x0 = int(x0 + x0_ * w)
        x1 = int(x1 - x1_ * w)
        y0 = int(y0 + y0_ * h)
        y1 = int(y1 - y1_ * h)
        rect_w = x1 - x0
        rect_h = y1 - y0

        return x0, y0, rect_w, rect_h

    def in_process(self):
        img = self.scaled
        x0, y0, w, h = self.rect()

        cv2.rectangle(img, (x0, y0), (x0 + w, y0 + h), (0, 255, 0), 2)

        return img


    def grabcut(self):
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        iter_count = self.config['iter_count']
        img = self.scaled

        if self.config['gc_type'] == 'mask':
            mask = self.gc_mask()
            cv2.grabCut(img, mask, None, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_MASK)

        elif self.config['gc_type'] == 'rect':
            rect = self.rect()
            mask = np.zeros(self.scaled.shape[:2], np.uint8)
            cv2.grabCut(img, mask, rect, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)

        else:
            mask = np.zeros(self.scaled.shape[:2], np.uint8)
            h, w = self.scaled.shape[:2]
            rect = 1, 1, w, h
            cv2.grabCut(img, mask, rect, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        gc_img = img * mask2[:, :, np.newaxis]

        return gc_img

    def grabcut_cleanup(self):
        img = cv2.cvtColor(self.grabcut(), cv2.COLOR_BGR2GRAY)

        h = int(img.shape[0] * self.config['k_scale'])
        w = int(img.shape[1] * self.config['k_scale'])

        kernel = np.ones((w, h), np.uint8)

        opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        return opened

    def mip_bbox(self):
        mask = self.grabcut_cleanup()
        mask = cv2.resize(mask, dsize=(0, 0), fx=1/self.scale, fy=1/self.scale)

        return calculate_bbox(mask)


class StereoPair:
    def __init__(self, config):
        self.config = config
        self.img = Image.open(config['path'])
        self.card_bb = config['card_bb']
        self.cropped = self.img.crop((self.card_bb[0],
                                      self.card_bb[1],
                                      self.card_bb[2],
                                      self.card_bb[3]))

    def channel_split(self, img):
        method = self.config['mip_channel_split']
        img = single_channel(img, method)

        return Image.fromarray(img)

    def slice_horizontal(self, img):
        """Middle third horizontally"""
        w, h = img.size
        slice = img.crop((0, np.round(h * 1 / 3), w, np.round(h * 2 / 3)))

        return slice

    def slice_vertical(self, img):
        """Middle third vertically"""
        w, h = img.size
        slice = img.crop((np.round(w * 1 / 3), 0, np.round(w * 2 / 3), h))

        return slice

    def feature_highlight(self, img):
        w, h = img.size
        method = self.config['mip_image_features']
        if method == 'fft':
            if w > h:
                axis = 1
                l = w
            else:
                axis = 0
                l = h
            filtered = fft_filter(np.asarray(img), axis, l)

        elif method == 'hog':
            _, filtered = hog(img, orientations=6, pixels_per_cell=(16, 16),
                              cells_per_block=(1, 1), visualize=True)

        elif method == 'sobel':
            filtered = sobel_v(img)

        else:
            filtered = img

        return filtered

    def w_features(self):
        img = self.channel_split(self.cropped)

        img_w = self.slice_horizontal(img)
        img_w = self.feature_highlight(img_w)

        return Image.fromarray(img_w * 255).convert('L')

    def get_peaks(self):
        # img = self.cropped()
        img = self.channel_split(self.cropped)
        w, h = img.size

        img_w = self.slice_horizontal(img)
        img_h = self.slice_vertical(img)

        img_w = self.feature_highlight(img_w)
        img_h = self.feature_highlight(img_h)

        x_plot = flatten(img_w, 0)
        y_plot = flatten(img_h, 1)

        x_plot = x_bias_curve(x_plot) * x_plot
        y_plot = y_bias_curve(y_plot) * y_plot

        x_peaks = find_peaks(x_plot)[0]
        x0, x1 = return_x_bounds(x_peaks, w, x_plot)

        y_peaks = find_peaks(y_plot)[0]
        y0, y1 = return_y_bounds(y_peaks, y_plot, h)

        return x0, x1, y0, y1

    def mip_bbox(self):
        peaks = self.get_peaks()

        return {'x0': int(peaks[0]),
                'x1': int(peaks[1]),
                'y0': int(peaks[2]),
                'y1': int(peaks[3])}


def flatten(img, axis):
    img_sum = np.sum(img, axis=axis)
    img_diff = np.abs(np.diff(img_sum))

    # copy
    x_plot = img_diff[:]

    # remove values below the standard deviation
    x_plot[x_plot < np.std(x_plot)] = 0

    # pad out to full length after differentiation
    x_plot = np.append(x_plot, 0)

    return x_plot


def just_edge_peaks(peaks, width):
    # left value is < 30% width
    # right value is > 70% width
    x0_locs = np.round(0.3 * width)
    x1_locs = np.round(0.7 * width)

    x0_pool = peaks[peaks < x0_locs]
    x1_pool = peaks[peaks > x1_locs]

    return (x0_pool, x1_pool)


def best_peaks(x0_pool, x1_pool, card_width, plot):
    # Make all combinations of potential peaks
    largest_pool = np.max([len(x0_pool), len(x1_pool)])
    combinations = np.array(np.meshgrid(x0_pool, x1_pool)).T.reshape(-1, largest_pool)

    if len(x0_pool) > 1 & len(x1_pool) > 1:
        # Test if center (simplified formula) is near 85% image center
        img_pair_size = (combinations[:, 1] - combinations[:, 0]) / card_width
        mid_truth = np.greater(img_pair_size, np.ones_like(img_pair_size) * 0.85)

        # Test if left edge strip + right edge of image pair is near full image size
        est_card_size = (combinations[:, 1] + combinations[:, 0]) / card_width
        size_truth = np.isclose(est_card_size, np.ones_like(img_pair_size), rtol=0.02)

        # Find pairs passing both tests
        pool_truth = np.logical_and(mid_truth, size_truth)
        num_passed = np.sum(pool_truth)
    else:
        num_passed = 0

    # TODO:
    # investigate ways of dealing with variations of 
    # what happens for variations of pair testing
    # original writeup showed handling pair match passing
    # only one test use the 80% rule

    if num_passed == 1:
        best_combo = combinations[pool_truth == True]
        x0 = best_combo[0][0]
        x1 = best_combo[0][1]

    if num_passed > 1:
        # narrow down x0_pool and x1_pool from all which passed both tests
        # print('num passed is {}'.format(num_passed))
        best_combos = combinations[pool_truth == True]
        x0_list = best_combos[:, 0]
        x1_list = best_combos[:, 1]
        # x0 = np.max(x0_list)
        # x1 = np.min(x1_list)

        peak_vals0 = [plot[i] for i in x0_list]
        idx = np.argmax(peak_vals0)
        x0 = x0_list[idx]

        peak_vals1 = [plot[i] for i in x1_list]
        idx = np.argmax(peak_vals1)
        x1 = x1_list[idx]

    else:
        # Choose Max peak values
        peak_vals0 = [plot[i] for i in x0_pool]
        if len(peak_vals0) > 0:
            idx = np.argmax(peak_vals0)
            x0 = x0_pool[idx]
        else:
            # failsafe value of average x0
            x0 = 0.0865 * card_width

        peak_vals1 = [plot[i] for i in x1_pool]
        if len(peak_vals1) > 0:
            idx = np.argmax(peak_vals1)
            x1 = x1_pool[idx]
        else:
            # failsafe value of average x1
            x1 = 0.9143 * card_width

    return x0, x1


def return_x_bounds(peaks, width, plot):
    num_peaks = len(peaks)

    if num_peaks < 2:
        # Failsafe, return average results
        x0 = np.round(width * 0.1)
        x1 = np.round(width * 0.9)
        # print('used failsafe')
    elif num_peaks == 2:
        # Twin Peaks found
        x0 = peaks[0]
        x1 = peaks[1]
        # print('twin peaks')
    else:
        # pare down list to get most likely right and left values
        x0_pool, x1_pool = just_edge_peaks(peaks, width)
        x0, x1 = best_peaks(x0_pool, x1_pool, width, plot)

    return x0, x1


def special_ycbcr(img):
    # Combination of Cb and Cr channels
    ycbcr = color.rgb2ycbcr(img)

    cb = ycbcr[:, :, 1]
    cr = ycbcr[:, :, 2]

    cb_i = np.max(cb) - cb
    combo = cb_i + cr

    combo_norm = combo / np.max(combo)

    return combo_norm


def get_diff_peaks(img, axis):
    # return the absolute value of the differential of the sum of image columns
    # axis is 0 for width and 1 for height images
    
    # TESTING
    hsv = color.rgb2hsv(img)
    sat = hsv[:, :, 1]
    combo_norm = sat / np.max(sat)

    # combo_norm = special_ycbcr(img)
    # filter
    # combo_norm = fft_filter(combo_norm, axis, 60)
    _, combo_norm = hog(combo_norm, orientations=6, pixels_per_cell=(16, 16),
                    cells_per_block=(1, 1), visualize=True)
    # combo_norm = sobel_v(combo_norm)

    combo_sum = np.sum(combo_norm, axis=axis)
    combo_diff = np.abs(np.diff(combo_sum))

    # filter
    x_plot = combo_diff

    # remove values below the standard deviation
    x_plot[x_plot < np.std(x_plot)] = 0

    # pad out to full length after differentiation
    x_plot = np.append(x_plot, 0)

    # mean filter
    smoothed = medfilt(x_plot, kernel_size=3)

    return smoothed


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

    # Make graph of brightnesses
    intensities_w = get_diff_peaks(w_slice, 0)

    # Bias the curve
    bias_term = x_bias_curve(intensities_w)
    biased_w = bias_term * intensities_w

    # Get peaks
    peaks = find_peaks(biased_w)[0]

    x0, x1 = return_x_bounds(peaks, w, biased_w)

    return x0, x1


def return_y_bounds(peaks, biased_h, height):
    y0_pool, y1_pool = just_edge_peaks(peaks, height)

    # TODO:
    # Try zero cases with 0 and height instead of 10/90%

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

    # Make graph of brightnesses
    intensities_h = get_diff_peaks(h_slice, 1)

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
