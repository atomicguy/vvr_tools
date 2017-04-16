function [tList, mid_index] = midpointMath(im_grey, image_size, regions, num_steps)
%%MIDPOINTMATH sets up structure tList of rectangles dividing an image

    % set generic start_size and step_size to create generic case
    if exist('num_steps','var') == 0
        num_steps = 10;
    end

    img_w = image_size(2);
    img_h = image_size(1);
%     feature_count = length(vPoints);
    
    img_third = floor(img_w/3);
    
    step_size = floor(img_third / num_steps);
    
    tList = struct('sectionA',[], 'sectionB', [],'featuresA',[], 'featuresB', [], 'matches', []);
    
    n = 1;
    k = 0;
    
    while n <= num_steps
        % Section A is a rectangle origin (0,0), initially sized width/3
        % Section B is a rectangle origin pinned to right edge of Section A
        sA = [0,0, img_third + (step_size *k) ,img_h];
        sB = [sA(3),0, img_w - sA(3), img_h];
        
        tList(n).sectionA = sA;
        tList(n).sectionB = sB;
        
        % segment Regions acording to section
        
        tList(n).featuresA = regions(regions.Location(:,1)<sA(3));
        tList(n).featuresB = regions(regions.Location(:,1)>sA(3));
        
        [regionsA, ~] = extractFeatures(im_grey,tList(n).featuresA);
        [regionsB, ~] = extractFeatures(im_grey,tList(n).featuresB);

        tList(n).matches = matchFeatures(regionsA,regionsB);
        tList(n).matches = length(tList(n).matches);
        
        k = k + 1;
        n = n + 1;
    end;
    
    matches = {};
    matches = {tList(1:end).matches};
    matches = cell2mat(matches);
    [~, mid_index] = max(matches);
    
end
        


        % load MSER features into appropriate cells
        
        
% function [featuresA, featuresB] = split_features(sB, tList, vPoints, feature_count)
% 
%     n_max = feature_count;
%     n = 1;
%     
%     while n <= n_max
%         if vPoints.Location(n,1) < sB(1)
%             tList(n).featuresA = vPoints(n);
%         else
%             tList(n).featuresB = vPoints(n);
%         end
%         n = n+1;
%     end
% 
% end
        
%         imA = imcrop(im_grey,sA);
%         imB = imcrop(im_grey,sB);
%         
%         briskA = detectBRISKFeatures(imA);
%         briskB = detectBRISKFeatures(imB);
%         
%         disp(['Features Detected in run: ',int2str(n)]);
%         
%         [featuresA, pointsA] = extractFeatures(im_grey,briskA);
%         [featuresB, pointsB] = extractFeatures(im_grey,briskB);
%         
%         tList(n).featuresA = featuresA;
%         tList(n).featuresB = featuresB;
%         tList(n).pointsA = pointsA;
%         tList(n).pointsB = pointsB;
%         
%         [indexPairs, matchmetric] = matchFeatures(featuresA,featuresB);
%         
%         tList(n).matches = [indexPairs];
%         tList(n).metrics = [matchmetric];
        
%         m = 1;
%     
%         while m <= feature_count
%             if vPoints.Location(m,1) < sB(1)
%                 tList(n).featuresA = vPoints(m);
%                 disp([int2str(m),' is in A.',int2str(n)]);
%             else
%                 tList(n).featuresB = vPoints(m);
%                 disp([int2str(m),' is in B.',int2str(n)]);
%             end
%             m = m+1;
%         end