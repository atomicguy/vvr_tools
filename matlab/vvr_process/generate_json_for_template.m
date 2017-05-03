clear; clc;

rootDir = fullfile(filesep,'Volumes','Go','images_to_run',filesep);
imDir = fullfile(rootDir,'images');

load('nypl_stereoview_db');

imSet = imageSet(imDir);
num_imgs = imSet.Count;
pathLength = numel(char(imDir))+2;

json_blob = struct('imageLoc',[],'imageName',[],'imageUUID',[],'imageIndex',[],'delineator',[]);

for n = 1:num_imgs
    
    try
        image_original = read(imSet,n);
        image_path = imSet.ImageLocation{n};
        image_id = image_path(pathLength:end-6);

        [~,db_index] = ismember(image_id,nyplpddb.ImageID);

        try % pull name from table
            image_id = char(nyplpddb.UUID(db_index));
            image_title = char(nyplpddb.Title(db_index));
        catch
            image_id = ['unkown',int2str(n)];
            image_title = ['unknown ',int2str(n)];
        end

        disp(['data gathered for ',image_id]);

        json_blob(n).imageLoc = [image_id,'.jpg'];
        json_blob(n).imageName = image_title;
        json_blob(n).imageUUID = image_id;
        json_blob(n).imageIndex = n;

        if n < num_imgs
            json_blob(n).delineator = ',';
        else
            json_blob(n).delineator = '';
        end  
    catch
        disp('error processing image');
    end
end

try
    savejson('cards',json_blob,[rootDir,'imagelist','.json']);
catch
    disp('error saving json file');
end