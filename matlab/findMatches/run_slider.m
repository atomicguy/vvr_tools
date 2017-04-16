[regions, grey_image, image_dimensions] = prep_image('G91F174_067F.jpg');

n = 0;
num_parts = 7;
image_half = round(image_dimensions(2)/2);
window_size = round(image_dimensions(2)/num_parts);
image_h = image_dimensions(1);
numsteps = round(image_dimensions(2)/2 - image_dimensions(2)/num_parts);
matchRank = [];

while n < numsteps

    [window1, window2] = window_setup(image_dimensions, num_parts, n);

    [w1xv, w1yv] = rect2poly(window1);
    [w2xv, w2yv] = rect2poly(window2);

    features_w1 = getWindowedFeatures(regions, grey_image, w1xv, w1yv );
    features_w2 = getWindowedFeatures(regions, grey_image, w2xv, w2yv );

    isMatch = matchFeatures(features_w1, features_w2);
    
    isMatch = length(isMatch);
    
    matchRank(n+1) = isMatch;
    
    disp(['match rank of step ',int2str(n), ' is ', int2str(isMatch)]);

    n = n + 5;
end

[maxVal, indexN] = max(matchRank);

part1 = imcrop(grey_image,[image_half - window_size, 0, window_size, image_h]);
part2 = imcrop(grey_image,[image_dimensions(2) - window_size - indexN, 0, window_size, image_h]);

imshow([part1,part2]);