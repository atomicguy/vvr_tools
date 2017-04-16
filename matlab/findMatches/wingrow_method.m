% read in image and prep it

clear;

im_url = 'G91F173_114F.tiff';

[im_grey, image_size, regions] = prep_image(im_url);

% wList = make_growindow(im_size);

[testSets, I] = midpointMath(im_grey, image_size, regions); 

% n = 1;
% matches = [];
% 
% while n<=10
%     matches(n) = testSets(n).matches;
%     n = n+1;
% end
% 
% [M,I] = max(matches);

imshow(imcrop(im_grey,testSets(I).sectionB));



%% Demonstration Zone

imA = imcrop(im_grey,testSets(I).sectionA);
imB = imcrop(im_grey,testSets(I).sectionB);

[regionsA, vpointsA] = extractFeatures(im_grey,testSets(I).featuresA);
[regionsB, vpointsB] = extractFeatures(im_grey,testSets(I).featuresB);

indexPairs = matchFeatures(regionsA,regionsB);

matchedPoints1 = vpointsA(indexPairs(:,1),:);
matchedPoints2 = vpointsB(indexPairs(:,2),:);

figure; ax = axes;
showMatchedFeatures(im_grey,im_grey, matchedPoints1, matchedPoints2);

%%

imshow(im_grey); hold on;
plot(testSets(2).featuresB);

hold off;

%% check on most likely candidate


candidate = 6;

% imshow([imcrop(im_grey,myList(iteration).sectionA),ones(image_size(1),20),imcrop(im_grey,myList(iteration).sectionB)]);

imA = imcrop(im_grey,testSets(candidate).sectionA);
imB = imcrop(im_grey,testSets(candidate).sectionB);

imshow([imA,ones(image_size(1),20),imB]);


