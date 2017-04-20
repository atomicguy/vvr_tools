function [ crop_points, partA, partB, bias_term, smooth_plot, xplotC ] = pickJustXpeaks( stereocard, cropYCbCr )
    
    imsize = size(stereocard);
    
    % slice rows from center of image for testing
    im_quarter = floor(imsize(1)/4);
    im_slice = cropYCbCr(im_quarter:3*im_quarter,:,:);
    
    % Break out YCbCr channels
    im_y  = im_slice(:,:,1);
    im_cb = im_slice(:,:,2);
    im_cr = im_slice(:,:,3);
    
    % Combine to emphasize diff between card and image
    partA = mat2gray(im_y);
    partB = max(im_cb(:)) - im_cb;
    partB = partB + im_cr;
    partB = mat2gray(partB);
    
    xplotA = abs(diff(sum(partA(1:end,:))));
    xplotB = abs(diff(sum(partB(1:end,:))));
    
    xplotC = xplotA + xplotB;
    
    xplot = xplotC;
    xplot(xplot<std(xplot)) = 0;
    xplot = medfilt1(xplot);

    plength = numel(xplot);
    
    % measurements indicate the following values for biasing plots
    % (for standardized plot of [1:1000]
    %
    %   A_l = 4.18
    %  mu_l = 86.5
    % sig_l = 26.6
    %
    %   A_r = 3.00
    %  mu_r = 914.3
    % sig_r = 25.0
    %
    
    bias_values = [4.18, 86.5, 26.6; 3.00, 914.3, 25.00];
    
    % convert into percentages to scale for any curve
    
    bias_values = bias_values/1000;
    
    % now scale for current image
    
    bv = bias_values * plength;
    
    l_bias = bv(1,1) * normpdf(1:plength, bv(1,2), bv(1,3));
    r_bias = bv(2,1) * normpdf(1:plength, bv(2,2), bv(2,3));

    bias_term = l_bias+r_bias;

    biased_plot = xplot.*bias_term;

    sampleSize = round(plength/500);
    coefSample = ones(1, sampleSize)/sampleSize;

    smooth_plot = filter(coefSample, 1, biased_plot);

    [pks,locs] = findpeaks(smooth_plot,'MinPeakHeight',mean(smooth_plot));

    % plotting peaks on zero line for ease of indexing
    plotline = zeros(plength,1);
    plotline(locs) = pks;

    % how many peaks were found?
    peak_count = numel(pks);

    % Establish how many peaks have been identified to pass to switch   
    found_peaks = 0;
    if peak_count<2
        found_peaks = 0;
    elseif peak_count == 2
        found_peaks = 2;
    elseif peak_count > 2
        found_peaks = 3;
    end
    
    switch found_peaks
        case 0 % Failsafe
            x1 = round(0.1*imsize(2));
            x2 = round(0.9*imsize(2));
        case 2 % Twin Peaks Identified
            x1 = locs(1);
            x2 = locs(2);
        case 3
            % find 30% and 70% x points
            % left value will be < 30% width
            % right value will be > 70% width
            x1locs = floor(0.3*numel(plotline));
            x2locs = floor(0.7*numel(plotline));
            
            % Narrow down the peak list
            num_x1s = numel(locs(locs<x1locs));
            num_x2s = numel(locs(locs>x2locs));
            x1_pool = locs(1:num_x1s);
            x2_pool = locs(end-num_x2s+1:end);


            % find percent diff with image midpoint for all x1,x2 pairs     
            test_grid_mids = abs(bsxfun(@minus,x1_pool,x2_pool'))./imsize(2);
            mid_find = find(test_grid_mids > 0.7);


            % find (x1+x2)/width for all pairs
            test_grid_size = bsxfun(@plus,x1_pool,x2_pool')./imsize(2);
            size_find = find(test_grid_size > 0.98 & test_grid_size < 1.02);


            % narrow the pool to only pairs which fulflill both tests
            kiddie_pool = intersect(mid_find,size_find);

            if numel(kiddie_pool) == 0
                % if no intersections, backup to midpoint results
                kiddie_pool = mid_find;
                [i1,i2] = ind2sub(size(test_grid_mids),kiddie_pool);
            elseif numel(kiddie_pool) > 0
                [i1,i2] = ind2sub(size(test_grid_mids),kiddie_pool);
            end

            x1 = x1_pool(i2);
            x1 = unique(x1);
            x2 = x2_pool(i1);
            x2 = unique(x2);


            % if multiple candidate pair, highest combined peak hight wins
            % This is a quick way to identify the two highest peaks without
            % having to do a set of max tests
            if numel(x1)>1 || numel(x2)>1
                x1_pks = plotline(x1);
                x2_pks = plotline(x2);
                reality_test = bsxfun(@plus,x1_pks,x2_pks');
                [~,ind] = max(reality_test(:));
                [ir1,ir2] = ind2sub(size(reality_test),ind);
                x1 = x1(ir1);
                x2 = x2(ir2);
            end
    end

    crop_points = [x1,x2];

end
