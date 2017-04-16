% calculate three x values from bounding box data

roimat = [xrois.objectBoundingBoxes];

x1 = roimat(1,:);
x2 = roimat(2,:);
x3 = roimat(3,:);

x1 = x1(1:4:end)-round(x1(3:4:end)/2);
x2 = x2(1:4:end)-round(x2(3:4:end)/2);
x3 = x3(1:4:end)-round(x3(3:4:end)/2);

immat = {xrois(1:end).imageFilename};

numim = length(xrois);
im_ws = {};
trueTable = zeros(numim,1000);

n = 1;

while n <= numim
    info = imfinfo(immat{n});
    im_ws{n} = info.XResolution;
    
    im_temp = zeros(1,info.XResolution);
    
    im_temp(1,x1(n)) = 1;
    im_temp(1,x2(n)) = 1;
    im_temp(1,x3(n)) = 1;
    
    im_stand = resample(im_temp,1000,info.XResolution);
    im_stand = abs(im_stand);
    
    trueTable(n,:) = im_stand;
    
    n = n+1;
end