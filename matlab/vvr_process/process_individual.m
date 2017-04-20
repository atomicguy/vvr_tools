%% Just extract Left and Right Pair

clear;clc;

image_path = fullfile('~','Desktop','ferris_wheel','8282_Ferris_Wheel.jp2');

[imL, imR, ~, ~] = just_lr_extract(image_path);

%% Extract LR pair and graphs and friends

clear;clc;

image_path = fullfile('~','Desktop','ferris_wheel','8282_Ferris_Wheel.jp2');
dirOut = fullfile('~','Desktop','ferris_wheel','output',filesep);

    try
        image_original = imread(image_path);
        image_id = ['8282_Wheel'];

        [ image_card, image_pair, image_left, image_right, card_gray, sliceBW, comboXstrip, xplot, xpeaks, smooth_plot, yplot, y_cut_peaks] = imDataExtract( image_path );
        [imleft,imright] = imbalancethresh(image_left,image_right);

        imwrite(image_left,[dirOut,image_id,'_L.jpg']);
        imwrite(image_right,[dirOut,image_id,'_R.jpg']);
        imwrite(imleft,[dirOut,image_id,'_balanced_L.jpg']);
        imwrite(imright,[dirOut,image_id,'_balanced_R.jpg']);
        
        impair = cat(2,imleft,imright);
        
        imwrite(card_gray,[dirOut,image_id,'_01_sliceBW.png']);
        imwrite(comboXstrip,[dirOut,image_id,'_02_slice.png']);
        imwrite(xplot,[dirOut,image_id,'_03_xplot.png']);
        
        try
            imwrite(yplot,[dirOut,image_id,'_04_yplot.png']);
            tmpfigy = figure('Visible','off');
            plot(y_cut_peaks,'Color',[0.02, 0.59, 0.88],'LineWidth',2);
            axis off;
            Plot2LaTeX(tmpfigy,['figures',image_id,'_06_yplot']);
        catch
            disp('no yplot');
        end
        
        try
            tmpfigpks = figure('Visible','off');
            plot(xpeaks, 'Color', [0.02, 0.59, 0.88],'LineWidth',2);
            axis off;
            Plot2LaTeX(tmpfigpks,['figures',image_id,'_07_xpeaks']);
        catch
            disp('no x peak plot');
        end
        
        try
            tmpfig = figure('Visible','off');
            plot(smooth_plot,'Color',[0.02, 0.59, 0.88],'LineWidth',2);
            axis off;
            Plot2LaTeX(tmpfig,['figures',image_id,'_05_xplot']);
        catch
            disp('no xplot svg');
        end
        
        imwrite(image_card,[dirOut,image_id,'_card.jpg']);
        imwrite(image_pair,[dirOut,image_id,'_pair.jpg']);


    catch
        disp(['error processing ',image_id]);
    end

