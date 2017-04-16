function [img_gray, img_dims, regions] = prep_image(image_url)

    % read in image, convert to grayscale via lab

    test_img = imread(image_url);
    if size(test_img,3) > 1
%         lab_img = rgb2lab(test_img);
%         img_gray = mat2gray(lab_img(:,:,1));
        img_gray = rgb2gray(test_img);
    else
        img_gray = test_img;
    end;
    
%     img_gray = adapthisteq(img_gray);
    
    img_dims = size(img_gray);

    % get Features

    regions = detectSURFFeatures(img_gray);
    
%     [~, validPoints] = extractFeatures(img_gray, mser_regions);

end