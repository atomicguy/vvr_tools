
[featuresA, vpointsA] = extractFeatures(im_grey, testSets(I).featuresA);

featuresB = testSets(I).featuresB;

widthB = testSets(I).sectionB(3);
half_width = floor(widthB/2);

bx = testSets(I).sectionB(1);
by = 0;
bh = testSets(I).sectionB(4);

num_steps = 10;
step_size = floor(half_width/num_steps);

n = 1;
testFeatures = struct('bounds',[], 'features',[], 'matches', []);

while n <= num_steps
    test_width = widthB - step_size * n;
    testFeatures(n).bounds = [bx,by, test_width, bh];
    
    testX = bx + test_width;
    
    testFeatures(n).features = featuresB(featuresB.Location(:,1)<testX);
    
    [featuresTest, vpointsTest] = extractFeatures(im_grey, testFeatures(n).features);
    
    testFeatures(n).matches = numel(matchFeatures(featuresA, featuresTest));
    
    n = n+1;
end

edgeIndex = cell2mat({testFeatures(1:end).matches});

edgeLength = length(edgeIndex);
edgeMedian = median(edgeIndex);
num_on_right = sum(edgeIndex<edgeMedian);
num_on_left = sum(edgeIndex>edgeMedian);

if num_on_right == num_on_left
    edgeI = num_on_left;
else
    num_medians = abs(num_on_left - num_on_right);
    centroid = ceil(num_medians/2);
    edgeI = num_on_left + centroid;
end

boundsB = testFeatures(edgeI).bounds;

% left image, left edge (right edge input needed)


[featuresB, vpointsB] = extractFeatures(im_grey, testFeatures(edgeI).features);

featuresA = testSets(I).featuresA;

widthA = testSets(I).sectionA(3);
half_width = floor(widthA/2);

ax = testSets(I).sectionA(1);
ay = 0;
ah = testSets(I).sectionA(4);

num_steps = 10;
step_size = floor(half_width/num_steps);

n = 1;
testFeatures = struct('bounds',[], 'features',[], 'matches', []);

while n <= num_steps
    test_width = widthA - step_size * n;
    test_x = ax + step_size * n;
    testFeatures(n).bounds = [test_x,by, test_width, bh];
    
    testX = test_x + test_width;
    
    testFeatures(n).features = featuresA(featuresA.Location(:,1)<testX);
    
    [featuresTest, vpointsTest] = extractFeatures(im_grey, testFeatures(n).features);
    
    testFeatures(n).matches = numel(matchFeatures(featuresB, featuresTest));
    
    n = n+1;
end

edgeIndex = cell2mat({testFeatures(1:end).matches});

edgeLength = length(edgeIndex);
edgeMedian = median(edgeIndex);
lowerVals = find(edgeIndex<edgeMedian);
higherVals = find(edgeIndex>edgeMedian);

num_medians = (edgeLength - length(lowerVals) - length(higherVals));

if num_medians > 1
    edgeI = length(higherVals) + ceil(num_medians/2);
else
    edgeI = edgeMedian;
end

boundsA= testFeatures(edgeI).bounds;

imshow([imcrop(im_grey,boundsA),ones(ah,20),imcrop(im_grey,boundsB)]);

%% demo



% imshow(imcrop(im_grey,testFeatures(6).bounds));




%function [tList] = rightEdge(im_grey, image_size, regions, num_steps)
% %%MIDPOINTMATH sets up structure tList of rectangles dividing an image
% 
%     % set generic start_size and step_size to create generic case
%     if exist('num_steps','var') == 0
%         num_steps = 10;
%     end
% 
%     img_w = image_size(2);
%     img_h = image_size(1);
% %     feature_count = length(vPoints);
%     
%     img_third = floor(img_w/3);
%     
%     step_size = floor(img_third / num_steps);
%     
%     tList = struct('sectionA',[], 'sectionB', [],'featuresA',[], 'featuresB', [], 'matches', []);
%     
%     n = 1;
%     k = 0;
%     
%     while n <= num_steps
%         % Section A is a rectangle origin (0,0), initially sized width/3
%         % Section B is a rectangle origin pinned to right edge of Section A
%         sA = [0,0, img_third + (step_size *k) ,img_h];
%         sB = [sA(3),0, img_w - sA(3), img_h];
%         
%         tList(n).sectionA = sA;
%         tList(n).sectionB = sB;
%         
%         % segment Regions acording to section
%         
%         tList(n).featuresA = regions(regions.Location(:,1)<sA(3));
%         tList(n).featuresB = regions(regions.Location(:,1)>sA(3));
%         
%         [regionsA, ~] = extractFeatures(im_grey,tList(n).featuresA);
%         [regionsB, ~] = extractFeatures(im_grey,tList(n).featuresB);
% 
%         tList(n).matches = matchFeatures(regionsA,regionsB);
%         tList(n).matches = length(tList(n).matches);
%         
%         k = k + 1;
%         n = n + 1;
%     end;
% end
        
