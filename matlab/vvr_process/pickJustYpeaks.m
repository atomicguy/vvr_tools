function [ crop_points, iflip, y_cut_peaks, bias_term ] = pickJustYpeaks( stereocard, cropYCbCr )
    
    imsize = size(stereocard);
    
    % slice columns from mid 80% for testing
    imlow  = floor(0.2*imsize(2));
    imhigh = ceil(0.8*imsize(2));
    
    im_slice = imcrop(cropYCbCr,[imlow,0,imhigh-imlow,imsize(2)]);
         
    im_cr = im_slice(:,:,3);
    im_cb = im_slice(:,:,2);
    
    % test ranges for next step
    is_gray = 'no';
    
    range_cb = range(im_cb(:));
    range_cr = range(im_cr(:));
    
    if range_cb < 42 && range_cr < 42
        is_gray = 'yes';
    end
    
    switch is_gray
        case 'no'
            im_cb = max(im_cb(:))-im_cb;
            img = im_cr + im_cb;
            
        case 'yes'
            img = im_slice(:,:,1);
    
    end
    
    iflip = imrotate(img,90);
    iflip = imclose(iflip,strel('diamond',9));
    
    im_sum = sum(iflip(1:end,:));
    yplot = abs(diff(im_sum,2));
    
    ystd = std(yplot);
    
    yplot(yplot<2*ystd) = 0;
    
    [smooth_plot,~] = envelope(yplot);
    smooth_plot = medfilt1(smooth_plot);
    
    plength = numel(smooth_plot);

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
    
    smooth_plot = bias_term .* smooth_plot;

    [pks,locs] = findpeaks(smooth_plot,'MinPeakHeight',mean(smooth_plot));

    % plotting peaks on zero line for ease of indexing
    plotline = zeros(plength,1);
    plotline(locs) = pks;

    % find 30% and 70% x points
    % left value will be < 30% width
    % right value will be > 70% width
    y1locs = floor(0.2*numel(plotline));
    y2locs = floor(0.8*numel(plotline));
    
    y_cut_peaks = zeros(plength,1);
    y_cut_peaks(1:y1locs) = smooth_plot(1:y1locs);
    y_cut_peaks(y2locs:end) = smooth_plot(y2locs:end);

    % how many peaks were found?
    peak_count = numel(pks);

    % If no peaks found, go to failsafe
    % If exactly 2 peaks found, use those
    % if more than 2 peaks found, continue to next logic block
    if peak_count<2
        % failsafe
        y1 = round(0.1*imsize(2));
        y2 = round(0.9*imsize(2));
    elseif peak_count == 2
        y1 = locs(1);
        y2 = locs(2);
    elseif peak_count > 2
        num_y1s = numel(locs(locs<y1locs));
        num_y2s = numel(locs(locs>y2locs));
        y1_pool = locs(1:num_y1s);
        y2_pool = locs(end-num_y2s+1:end);
    end

    y1_pool_group = cat(2,y1_pool',plotline(y1_pool));
    y2_pool_group = cat(2,y2_pool',plotline(y2_pool));
    
    [~,y1i] = max(y1_pool_group(:,2));
    [~,y2i] = max(y2_pool_group(:,2));
    
    y1 = y1_pool(1,y1i);
    y2 = y2_pool(1,y2i);
    
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



