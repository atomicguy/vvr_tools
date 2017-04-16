function [testR1, testR2] = window_setup(img_dims, fractional, offset)
%WINDOW_SETUP generates a fixed window from the midpoint of an image, and a shiftable window from the right edge
% img_dims are image dimensions
% fractional sets the size of the windows (width/fractional)
% offset slides the right most window

    img_width = img_dims(2);
    img_h = img_dims(1);
    img_mid = round(img_width/2);
    img_part = round(img_width/fractional);

    testR1 = [img_mid - img_part, 0, img_part, img_h];
    testR2 = [img_dims(2) - img_part - offset, 0, img_part, img_h];
end