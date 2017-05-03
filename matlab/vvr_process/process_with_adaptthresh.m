clear;clc;

load('nypl_stereoview_db');

rootDir = fullfile(filesep,'Volumes','Go','images_to_run');
imDir = fullfile(rootDir,'images',filesep);
cardsOut = fullfile(rootDir,'cards',filesep);
pairOut = fullfile(rootDir,'pairs',filesep);
lrpairsOut = fullfile(rootDir,'lrpairs',filesep);
stepsOut = fullfile(rootDir,'steps',filesep);

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

        [imcard, impair, imleft, imright, card_gray, sliceBW, comboXstrip, xplot, smooth_plot, yplot, y_cut_peaks] = imextract(image_path);
        [imleft,imright] = imbalancethresh(imleft,imright);

        impair = cat(2,imleft,imright);
        
        imwrite(card_gray,[stepsOut,image_id,'_01_sliceBW.png']);
        imwrite(sliceBW,[stepsOut,image_id,'_02_sliceBW.png']);
        imwrite(xplot,[stepsOut,image_id,'_03_xplot.png']);
        
        try
            imwrite(yplot,[stepsOut,image_id,'_04_yplot.png']);
            tmpfigy = figure('Visible','off');
            plot(y_cut_peaks,'Color',[0.02, 0.59, 0.88],'LineWidth',2);
            axis off;
            Plot2LaTeX(tmpfigy,['figures/',image_id,'_06_yplot']);
        catch
            disp('no yplot');
        end
        
        try
            tmpfig = figure('Visible','off');
            plot(smooth_plot,'Color',[0.02, 0.59, 0.88],'LineWidth',2);
            axis off;
            Plot2LaTeX(tmpfig,['figures/',image_id,'_05_xplot']);
        catch
            disp('no xplot svg');
        end
        
        imwrite(imcard,[cardsOut,image_id,'.jpg']);
        imwrite(impair,[pairOut,image_id,'.jpg']);

        imwrite(imleft,[lrpairsOut,'L_',image_id,'.jpg']);
        imwrite(imright,[lrpairsOut,'R_',image_id,'.jpg']);

    catch
        disp(['error processing ',image_id]);
    end
    
    try % generate json
        json_blob(n).imageLoc = [image_id,'.jpg'];
        try % find name
            json_blob(n).imageName = image_title;
            json_blob(n).imageUUID = image_id;
        catch
            disp('not in list');
        end
        json_blob(n).imageIndex = n;
        if n < num_img
            json_blob(n).delineator = ',';
        else
            json_blob(n).delineator = '';
        end
        
    catch
        disp('json creation error');
    end
    
end

reset(gcf);

savejson('cards',json_blob,[rootDir,'/imagelist.json']);

