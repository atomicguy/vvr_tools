clear;clc;

%load('nypl_stereoview_db');

rootDir = fullfile(filesep,'Volumes','Go','images_to_run');
imDir = fullfile(rootDir,'images',filesep);
%cardsOut = fullfile(rootDir,'cards',filesep);
%pairOut = fullfile(rootDir,'pairs',filesep);
lrpairsOut = fullfile(rootDir,'lrpairs',filesep);
%stepsOut = fullfile(rootDir,'steps',filesep);

% Collect image names, and number of images
imageNames = dir([imDir,'*.tiff']); 
imageList = {imageNames(1:end).name};
num_img = length(imageNames);

imageIDList = cell(num_img,1);
m = 1;
while m <= num_img
    imageIDList{m} = imageNames(m).name(1,1:end-5);
    m = m+1;
end


for n = 1:num_img
  disp(['working on image ',imageNames(n).name]);
    
    try % Read in Image
        image_path = [imDir,imageList{n}];
        image_id = imageNames(n).name(1:end-5);
        image_original = imread(image_path);
    catch
        disp('error reading image');
    end
    
    try
      
        [imcard, impair, imleft, imright, ~, ~, ~, ~, ~, ~, ~] = imextract(image_path);
        [imleft,imright] = imbalancethresh(imleft,imright);

        imwrite(imleft,[lrpairsOut,'L_',image_id,'.jpg']);
        imwrite(imright,[lrpairsOut,'R_',image_id,'.jpg']);

    catch
        disp(['error processing ',image_id]);
    end
    
   
    
end


