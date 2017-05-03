function [ scBox, Iycbcr, image_gray, sliceBW, isRGB ] = stereocardBox( image_original )
%STEREOCARDBOX returns a bounding box isolating a stereocard from
%background
    cardtic = tic;

    % Find dimensions to determine if RGB or Grayscale
    imD = size(image_original);
    imD = numel(imD);
    
    if imD > 2
        isRGB = 'true';
    else
        isRGB = 'false';
    end
    
    switch isRGB
        case 'true'
            Iycbcr = rgb2ycbcr(image_original);
            
            % Split out Cb channel and invert it so the card is white
            slice1 = Iycbcr(:,:,2);
            slice1 = max(slice1(:))-slice1;    
            slice2 = Iycbcr(:,:,3);

            cb_range = range(slice1(:));
            cr_range = range(slice2(:));
            
            image_gray = slice1 + slice2;
            image_gray = mat2gray(image_gray);

        case 'false'
            image_gray = mat2gray(image_original);
            fake_rgb = cat(3,image_gray,image_gray,image_gray);
            Iycbcr = rgb2ycbcr(fake_rgb);
    end
    
%     % Light on Dark or Dark on Light?
%     im_h = size(image_original,1);
%     im_w = size(image_original,2);
% 
%     w_deci = floor(im_w/10);
%     h_deci = floor(im_h/10);
% 
%     avg_bright = zeros(1,2);
% 
%     % Find brightness of edges
%     edge1 = image_gray(:,1:w_deci);
%     edge2 = image_gray(:,9*w_deci:end);
%     edges = cat(2,edge1,edge2);
%     avg_bright(1) = mean(edges(:));
% 
%     % Find mid/card brightness
%     center = image_gray(3*h_deci:7*h_deci,3*w_deci:7*w_deci);
%     avg_bright(2) = mean(center(:));
% 
%     % Returns 
%     % 1 if edges brigther
%     % 2 if interior brighter
%     [~,brighter] = max(avg_bright);
%             
%     switch brighter
%         case 1 % Light Card
%             % Calculate threshold, and convert to black and white
%             [level, EM] = graythresh(image_gray);
%             if EM > 0.5
%                 sliceBW = im2bw(image_gray, level);
%             else
%                 sliceBW = im2bw(image_gray);
%             end
% 
%             % Erode to quickly remove stray pixels
%             sliceBW = imerode(sliceBW,strel('diamond',11));
% 
%             % Find the non-zero values (i.e. the card)
%             [r,c] = find(sliceBW);
% 
%             % Bounding Box points are highest and lowest x/y values
%             x0 = min(c);
%             y0 = min(r);
%             w1 = max(c);
%             h1 = max(r);
% 
%         case 2 % Dark Card
%             % invert to get brighter image
%             image_indexing = 1-image_gray;
%             image_indexing = histeq(image_indexing);
%             image_indexing = im2bw(image_indexing);
%             image_indexing = imclearborder(image_indexing);
%             
%             % Morph clean-up
%             image_cleaned = imclose(image_indexing,strel('diamond',11));
%             image_filled = imfill(image_cleaned,'holes');
% 
%             % label bw regions
%             L = bwlabel(image_filled);
% 
%             % the most common label will be the card or the background
%             common_label = mode(L(:));
%             [r,c] = find(L==common_label);
% 
%             x0 = min(c);
%             y0 = min(r);
%             w1 = max(c);
%             h1 = max(r);
%             
%             if x0 == 1 || y0 == 1
%                 img_ind = L==common_label;
%                 img_ind = 1-img_ind;
%                 img_ind = imopen(img_ind,strel('diamond',9));
%                 
%                 [r,c] = find(img_ind);
%                 
%                 x0 = min(c);
%                 y0 = min(r);
%                 w1 = max(c);
%                 h1 = max(r);
%             end
%                 
%                 
%     end

    % Calculate threshold, and convert to black and white
    [level, EM] = graythresh(image_gray);
    if EM > 0.5
        sliceBW = im2bw(image_gray, level);
    else
        sliceBW = im2bw(image_gray);
    end

    % Erode to quickly remove stray pixels
    sliceBW = imerode(sliceBW,strel('disk',7));

    % Find the non-zero values (i.e. the card)
    [r,c] = find(sliceBW);

    % Bounding Box points are highest and lowest x/y values
    x0 = min(c);
    y0 = min(r);
    w1 = max(c);
    h1 = max(r);

    % Calculate width/height values for bounding box
    h0 = h1 - y0;
    w0 = w1 - x0;

    scBox = [x0,y0,w0,h0];
    
    cardtoc = toc(cardtic);
    disp(['cropbox cropping took: ',num2str(cardtoc)]);

end

