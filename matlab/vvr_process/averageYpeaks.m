function [ crop_points ] = averageYpeaks( stereocard )
    
    imsize = size(stereocard);
  
    plength = imsize(2);

    % measurements indicate the following values for biasing plots
    % (for standardized plot of [1:1000]
    %
    %   A_l = 4.4
    %  mu_l = 42.0
    % sig_l = 19.6
    %
    %   A_r = 8.8
    %  mu_r = 944.7
    % sig_r = 17.9
    %
    
    bias_values = [4.4, 42, 25; 8.8, 944.7, 25];
    
    % convert into percentages to scale for any curve
    
    bias_values = bias_values/1000;
    
    % now scale for current image
    
    bv = bias_values * plength;
    
    l_bias = bv(1,1) * normpdf(1:plength, bv(1,2), bv(1,3));
    r_bias = bv(2,1) * normpdf(1:plength, bv(2,2), bv(2,3));

    bias_term = l_bias+r_bias;
    
    [~,locs] = findpeaks(bias_term);

        y1 = locs(1);
        y2 = locs(2);

    
    % if at this point there are no y1 values, the image is cropped to the
    % top
    if y1 > 0
        % nothing to see here, move along
    else
        y1 = 1;
    end
    
    % if at this point there are no y2 values, image is cropped at the
    % bottom
    if y2 > 0
        % nothing to see here, move along
    else
        y2 = imsize(1);
    end

    crop_points = [y1,y2];

end



