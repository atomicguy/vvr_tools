clear;clc;

load('nypl_stereoview_db');

rootDir = fullfile(filesep,'Volumes','Lexar 128','NYPL','Virginia');
imDir = fullfile(rootDir,'images',filesep);
outDir = fullfile(filesep,'Volumes','Lexar 128','VAQA','average_anaglyph',filesep);

imSet = imageSet(imDir);

length_filepath = numel(imDir)+1;
num_img = imSet.Count;

json_blob = [];
json_blob = struct('imageLoc',[],'imageName',[],'imageUUID',[],'imageIndex',[],'delineator',[]);

for n = 1:num_img
    
    try
        image_original = read(imSet,n);
        image_path = imSet.ImageLocation{n};
        image_id = image_path(length_filepath:end-6);
        
        [~,db_index] = ismember(image_id,nyplpddb.ImageID);
        
        try % pull name from table
            image_id = char(nyplpddb.UUID(db_index));
            image_title = char(nyplpddb.Title(db_index));
        catch
            image_id = ['unkown',int2str(n)];
            image_title = ['unknown ',int2str(n)];
        end
        
        disp(['starring image ',image_id]);
        disp(['n is ',int2str(n)]);
        
        try % Read in Image
            image_original = imread(image_path);
        catch
            disp('error reading image');
        end

        try % crop to original stereocard, flag non RGB
            [cropbox, Iycbcr, card_gray, sliceBW, ~] = stereocardBox(image_original);

            stereocard = imcrop(image_original,cropbox);
            cropYCbCr = imcrop(Iycbcr,cropbox);
        catch
            disp('error extracting stereocard');
        end

        image_card = stereocard;

        % Determine if image is already cropped as a result of prior step
        image_size = size(image_original);
        width_ratio = size(stereocard,2)/image_size(2);
        height_ratio = size(stereocard,1)/image_size(1);

        if width_ratio > 0.78
            x_case = 'needs_crop';
        else
            x_case = 'already_cropped';
        end

        if height_ratio > 0.7
            y_case = 'needs_crop';
        else
            y_case = 'already_cropped';
        end
        
         % Use exsiting edges if already cropped, otherwise calculate left/right edge pair
        switch x_case
            case 'already_cropped'
                xpoints = [1,size(stereocard,2)];

            case 'needs_crop'
                % Find the main pair of images
                try
                    [xpoints] = averageXpeaks(stereocard);
                catch
                    disp('error finding x points');
                end
        end

        switch y_case
            case 'already_cropped'
                ypoints = [1,size(stereocard,1)];

            case 'needs_crop'
                try
                   [ypoints] = averageYpeaks(stereocard);
                catch
                    disp('error finding y points');
                end
        end

        try
            x0 = xpoints(1);
            y0 = ypoints(1);
            w0 = xpoints(2)-xpoints(1);
            h0 = ypoints(2)-ypoints(1);
            corebox = [x0,y0,w0,h0];
        catch
            disp('error creating cropbox');
        end

        try
            image_pair = imcrop(stereocard,corebox);
        catch
            disp(['error cropping pairs']);
        end

        try
            imw = size(image_pair,2);
            halfw = floor(imw/2);

            image_left = image_pair(:,1:halfw,:);
            image_right = image_pair(:,halfw+1:2*halfw,:);

        catch
            disp(['error making left/right images']);
        end
        
        imCombo = imfuse(image_left,image_right,'ColorChannels','red-cyan');
        
        imwrite(imCombo,[outDir,image_id,'.jpg']);

    catch
        disp(['error processing ',image_id]);
    end
    
end


