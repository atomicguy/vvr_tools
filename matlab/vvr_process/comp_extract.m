function [ image_card, image_pair, image_left, image_right] = comp_extract( image_path )
%IMEXTRACT identifies and extracts the right and left images from a
%stereocard
    ttime = tic;
    
    disp('running imextract');

    try % Read in Image
        image_original = imread(image_path);
    catch
        disp('error reading image');
    end
    
    try % crop to original stereocard, flag non RGB
        [cropbox, Iycbcr, card_gray, sliceBW, ~] = stereocardBox(image_original);

        stereocard = imcrop(image_original,cropbox);
        cropYCbCr = imcrop(Iycbcr,cropbox);
    catch
        disp('error extracting stereocard');
    end
    
    image_card = stereocard;
    
    % Determine if image is already cropped as a result of prior step
    image_size = size(image_original);
    width_ratio = size(stereocard,2)/image_size(2);
    height_ratio = size(stereocard,1)/image_size(1);
    
    if width_ratio > 0.78
        x_case = 'needs_crop';
    else
        x_case = 'already_cropped';
    end
    
    if height_ratio > 0.7
        y_case = 'needs_crop';
    else
        y_case = 'already_cropped';
    end
        
    % Use exsiting edges if already cropped, otherwise calculate left/right edge pair
    switch x_case
        case 'already_cropped'
            xpoints = [1,size(stereocard,2)];
            [~,partA,partB,~,smooth_plot] = pickJustXpeaks(stereocard, cropYCbCr);
            comboXstrip = mat2gray(imadd(partA,partB));
            
        case 'needs_crop'
            % Find the main pair of images
            try
                [xpoints, partA, partB, ~, smooth_plot] = pickJustXpeaks(stereocard, cropYCbCr);
                comboXstrip = mat2gray(imadd(partA,partB));
            catch
                disp('error finding x points');
            end

    end
    
    switch y_case
        case 'already_cropped'
            ypoints = [1,size(stereocard,1)];
            [~, ~, y_cut_peaks, ~] = pickJustYpeaks(stereocard,cropYCbCr);

        case 'needs_crop'
            try
               [ypoints, ~, y_cut_peaks, ~] = pickJustYpeaks(stereocard, cropYCbCr);
               
            catch
                disp('error finding y points');
            end
    end
 
    try
        x0 = xpoints(1);
        y0 = ypoints(1);
        w0 = xpoints(2)-xpoints(1);
        h0 = ypoints(2)-ypoints(1);
        corebox = [x0,y0,w0,h0];
    catch
        disp('error creating cropbox');
    end
    
    try
        image_pair = imcrop(stereocard,corebox);
    catch
        disp(['error cropping pairs']);
    end
    
    try
        imw = size(image_pair,2);
        halfw = floor(imw/2);

        image_left = image_pair(:,1:halfw,:);
        image_right = image_pair(:,halfw+1:2*halfw,:);
    
    catch
        disp(['error making left/right images']);
    end
    
    elapsed_time = toc(ttime);
%     disp(['Total Time: ',num2str(elapsed_time)]);

end

