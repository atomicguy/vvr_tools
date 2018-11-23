import cv2
import numpy as np
from skimage import color
from skimage.filters import threshold_otsu, threshold_mean, threshold_local, threshold_minimum
from skimage.morphology import diamond, binary_erosion


def single_channel(img, method):
    """Convert image to single channel

    :param img: PIL image
    :param method: single channel method
    :return: single channel iamge
    """
    img = np.asarray(img)

    if method == 'cb':
        ycbcr = color.rgb2ycbcr(img)
        gray = ycbcr[:, :, 1]

    elif method == 'cr':
        ycbcr = color.rgb2ycbcr(img)
        cr = ycbcr[:, :, 2]
        gray = np.max(cr) - cr

    elif method == 'cbcr':
        ycbcr = color.rgb2ycbcr(img)
        cb = ycbcr[:, :, 1]
        cr = ycbcr[:, :, 2]
        gray = cr + (np.max(cb) - cb)

    elif method == 'sat':
        hsv = color.rgb2hsv(img)
        gray = hsv[:, :, 1]

    else:
        hsv = color.rgb2hsv(img)
        gray = hsv[:, :, 2]

    return gray


def binary(img, method):
    """Threshold image

    :param img: grayscale image (numpy array)
    :param method: thresholding method
    :return: binary image
    """
    if method == 'otsu':
        thresh = threshold_otsu(img)
        binary = img > thresh

    elif method == 'mean':
        thresh = threshold_mean(img)
        binary = img > thresh
        binary = 1 - binary

    elif method == 'local':
        thresh = threshold_local(img, 35, offset=10)
        binary = img > thresh

    else:
        thresh = threshold_minimum(img)
        binary = img > thresh

    return binary


def filter_binary(img, size):
    selem = diamond(size)
    cleaned = binary_erosion(img, selem)

    return cleaned


def fft_filter(img, axis, mask_width):
    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)

    rows, cols = img.shape
    crow, ccol = int(rows/2), int(cols/2)

    # create a mask first, center square is 1, remaining all zeros
    mask = np.ones((rows,cols,2),np.uint8)
    x = int(mask_width / 2)
    if axis == 1:
        mask[crow-x:crow+x, :] = 0
    else:
        mask[:, ccol-x:ccol+x] = 0

    # apply mask and inverse DFT
    fshift = dft_shift*mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])

    return img_back / np.max(img_back)
