imDir = fullfile(filesep,'Volumes','Media', 'NYPLCollection','Florida', 'jpegs', filesep);
% imDir = fullfile(filesep,'Volumes','Lexar 128','control_samples',filesep);
outDir = fullfile(filesep,'Users','atom', 'ownCloud','FL_lines', filesep);

imageNames = dir([imDir,'*.jpg']);

imageList = {imageNames(1:end).name};
numImages = length(imageList);

n = 1;
while n <=numImages
    

    image_path = [imDir,imageList{n}];
    image_pixels = imread(image_path);

    RGB = image_pixels;

    ymax = size(image_pixels,1);

    t = possibleSolve;
    qmax = length(t);
    q = 1;

    while q<=qmax
%         disp(['q = ',int2str(q)]);
        RGB = insertShape(RGB,'line',[t(q,1),0,t(q,1),ymax],'Color','red');
        RGB = insertShape(RGB,'line',[t(q,2),0,t(q,2),ymax],'Color','green');
        RGB = insertShape(RGB,'line',[t(q,3),0,t(q,3),ymax],'Color','blue');
%         imwrite(RGB,[outDir,int2str(n),'.jpg']);
        imshow(RGB);
        q = q+1;
    end
    n=n+1;
end
