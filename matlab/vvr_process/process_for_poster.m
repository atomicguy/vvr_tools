clear;clc;

rootDir = fullfile(filesep,'Volumes','BlueBox','demos');
imDir = fullfile(rootDir,'images',filesep);
cardsOut = fullfile(rootDir,'cards',filesep);
pairOut = fullfile(rootDir,'pairs',filesep);
lrpairsOut = fullfile(rootDir,'lrpairs',filesep);
stepsOut = fullfile(rootDir,'steps',filesep);

imSet = imageSet(imDir);

length_filepath = numel(imDir)+1;
num_img = imSet.Count;


for n = 1:num_img
    
    try
        image_original = read(imSet,n);
        image_path = imSet.ImageLocation{n};
        image_id = image_path(length_filepath:end-6);
        
        disp(['starring image ',image_id]);
        disp(['n is ',int2str(n)]);

        [imcard, impair, imleft, imright] = comp_extract(image_path);
        [imleft,imright] = imbalancethresh(imleft,imright);

        im_anaglyph = imfuse(imleft, imright, 'ColorChannels', 'red-cyan');
        imwrite(im_anaglyph,[cardsOut,'kg_anaglyph',image_id,'.png']);
        
        % Average Values Case
        [~,~,avleft,avright] = comp_extract_avgdata(image_path);
        [avleft,avright] = imbalancethresh(avleft,avright);
        
        av_anaglyph = imfuse(avleft, avright, 'ColorChannels', 'red-cyan');
        imwrite(av_anaglyph,[cardsOut,'kb_anaglyph',image_id,'.png']);
        

    catch
        disp(['error processing ',image_id]);
    end
    
    
end

reset(gcf);

