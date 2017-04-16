function [matchMap] = feature_sampler(im_path, part_scale, num_samples)

image = imread(im_path);
image_gray = rgb2gray(image);

sf = detectSURFFeatures(image_gray);

imsize = size(image_gray);
im_h = imsize(1);
im_w = imsize(2);

matchMap = zeros(imsize);

% parts = [5,10];
scale_h = floor(im_h/part_scale);
scale_w = floor(im_w/part_scale);
h_10 = floor(scale_h/3);
w_10 = floor(scale_w/3);

h_min = scale_h - h_10;
h_max = scale_h + h_10;
w_min = scale_w - w_10;
w_max = scale_w + w_10;

% set up arrays of x,y coords for samples
% num_samples = 500;

x_rand = randi(im_w - w_max, num_samples, 1);
y_rand = randi(im_h - h_max, num_samples, 1);
w_rand = randi([w_min,w_max], num_samples, 1);
h_rand = randi([h_min,h_max], num_samples, 1);

% set up array of sample bounding boxes
samples = zeros(num_samples, 4);

samples(1:end,1) = x_rand(1:end);
samples(1:end,2) = y_rand(1:end);
samples(1:end,3) = w_rand(1:end);
samples(1:end,4) = h_rand(1:end);

n = 1;
m = num_samples;
nmax = num_samples;

% matchList = struct('index', [], 'something', []);

while n <= nmax
    x1a = samples(n,1);
    x2a = samples(n,1) + samples(n,3);
    y1a = samples(n,2);
    y2a = samples(n,2) + samples(n,4);
    
    x1b = samples(m,1);
    x2b = samples(m,1) + samples(m,3);
    y1b = samples(m,2);
    y2b = samples(m,2) + samples(m,4);
    
    featuresA = sf(sf.Location(:,1)>x1a&sf.Location(:,1)<x2a&sf.Location(:,2)>y1a&sf.Location(:,2)<y2a);
    featuresB = sf(sf.Location(:,1)>x1b&sf.Location(:,1)<x2b&sf.Location(:,2)>y1b&sf.Location(:,2)<y2b); 
    
    [fA, ~] = extractFeatures(image_gray, featuresA);
    [fB, ~] = extractFeatures(image_gray, featuresB);
    
%     matchList(n).index = matchFeatures(fA, fB);
    iPairs = matchFeatures(fA, fB);
    value = length(iPairs);
    
    matchMap(y1a:y2a,x1a:x2a) = matchMap(y1a:y2a,x1a:x2a) + value;
    matchMap(y1b:y2b,x1b:x2b) = matchMap(y1b:y2b,x1b:x2b) + value;
    
    n = n+1;
    m = m-1;
end

% imshow(matchMap,linear_bmy_10_95_c78_n256);


% % % % % 
% image = imread('Sample4.jpg');
% 
% image_gray = rgb2gray(image);
% image_lab = rgb2lab(image);
% image_ycbcr = rgb2ntsc(image);
% 
% image_l = image_lab(:,:,1);
% image_y = image_ycbcr(:,:,1);
% 
% image_range = rangefilt(image);
% 
% image_rlab = rgb2lab(image_range);
% 
% % imshow(image_rlab(:,:,2),[]);
% % 
% 
% % 
% % [featureVectors, hogVisualization] = extractHOGFeatures(image);
% % 
% % figure(1);
% % imshow(image); hold on;
% % plot(hogVisualization);
% %%
% 
% image_adapt = adapthisteq(image_gray);
% 
% image_ent = entropyfilt(image_adapt);
% 
% image_mat = mat2gray(image_ent);
% 
% imshow(image_mat,viridis);
% %%
% 
% clear;clc;
% 
% image = imread('Sample3.jpg');
% 
% image_gray = rgb2gray(image);
% 
% 
% %% HOG Wild
% 
% [features, hogViz] = extractHOGFeatures(image);
% 
% points = detectSURFFeatures(image_gray);
% strongest = selectStrongest(points,100);
% 
% [hog2, validPoints, ptViz] = extractHOGFeatures(image, strongest);
% 
% figure(1);
% imshow(image); hold on;
% plot(ptViz, 'Color','green');


