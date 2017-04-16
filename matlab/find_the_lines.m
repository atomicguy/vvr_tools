clear;clc;

% set image directory path
imDir = fullfile(filesep,'Volumes','Lexar 128','NYPL','thedells',filesep);
imageNames = dir([imDir,'*.tiff']);
num_img = length(imageNames);

imageList = {imageNames(1:end).name};

outDir = fullfile(filesep,'Volumes','Public','edgeclip',filesep);

n = 1;


while n <= num_img
    image_name = [imDir,imageList{n}];
    image = imread(image_name);
    imedge = rangefilt(image);
    imedge = rgb2gray(imedge);
    
    im_size = size(imedge);
    im_width = im_size(2);
    im_height = im_size(1);
    
    im_accum = zeros(1,im_width);
    
    try
        k = 1;
        while k <= im_width
            im_accum(k) = median(imedge(:,k));
            k = k+1;
        end
        
        [M,I] = max(diff(im_accum(:)));
        
        try
            left_accum = zeros(1,I);
            m = 1;
            while m <= I
                left_accum(m) = median(imedge(:,m));
                m = m + 1;
            end
            
            [M1,I1] = max(diff(left_accum(:)));
            
        catch
            disp(['error finding left point on image ',image_name]);
        end
        
        try
            left_accum2 = zeros(1,I-I2);
            q = I2;
            while q <= left_accum2
                left_accum2(q) = median(imedge(:,q));
                q = q+1;
            end
            
            [M2,I2] = max(diff(left_accum2(:)));
        catch
            disp(['error finding 2nd left point on image ',image_name]);
        end
        
        cropped = imcrop(image,[0,0,I,im_height]);
        
        if exist('I2','var') == 1
            cropped = imcrop(cropped,[I2,0,I-I2,im_height]);
        else
            if exist('I1','var') == 1
                cropped = imcrop(cropped,[I1,0,I-I1,im_height]);
            end
        end
                
        imwrite(cropped,[outDir,imageNames(n).name(1:end-5),'.jpg']);
    catch
        disp(['error finding midpoint of image ',image_name]);
    end
    
    n = n+1;
end
