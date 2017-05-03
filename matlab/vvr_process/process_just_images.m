clear;clc;

rootDir = fullfile(filesep,'Volumes','Go','NYPL_Collection');
imDir = fullfile(rootDir,'images',filesep);
lrpairsOut = fullfile(rootDir,'LR_images',filesep);

imSet = imageSet(imDir);

length_filepath = numel(imDir)+1;
num_img = imSet.Count;

docNode = com.mathworks.xml.XMLUtils.createDocument('rndcollection');
rndcollection = docNode.getDocumentElement;
rndcollection.setAttribute('version','0.1');
xmlwrite('collection_info.xml',docNode);

for n = 1:1
    
     try
        image_original = read(imSet,n);
        image_path = imSet.ImageLocation{n};
        image_id = image_path(length_filepath:end-6);
        
        disp(['starring image ',image_id]);
        disp(['image ',int2str(n),', ',int2str(num_img-n),' left']);

        [~, ~, corebox, elapsed_time] = just_lr_extract(image_path);
        
        rndNode = xmlread('collection_info.xml');
        rndNode = rndNode.getDocumentElement;
        
        thisCard = rndNode.createElement('stereocard');
        thisCard.appendChild(rndNode.createTextNode(image_id));
        
        boxen = rndNode.createElement('boundingBox');
        boxen.appendChild(rndNode.createTextNode(corebox));
        
        etime = rndNode.createElement('elapsedTime');
        etime.appendChild(rndNode.createTextNode(elapsed_time));
        
        xmlwrite('collection_info.xml',rndNode);

    catch
        disp(['error processing ',image_id]);
    end
    
    try
        image_original = read(imSet,n);
        image_path = imSet.ImageLocation{n};
        image_id = image_path(length_filepath:end-6);
        
        disp(['starring image ',image_id]);
        disp(['image ',int2str(n),', ',int2str(num_img-n),' left']);

        [imleft, imright] = just_lr_extract(image_path);
        [imleft,imright] = imbalancethresh(imleft,imright);

        imwrite(imleft,[lrpairsOut,image_id,'_L.jpg']);
        imwrite(imright,[lrpairsOut,image_id,'_R.jpg']);

    catch
        disp(['error processing ',image_id]);
    end

end
