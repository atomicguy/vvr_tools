function windowedFeatures = getWindowedFeatures(mser_regions, img_gray, xv, yv)

    testRegion = mser_regions.Location;
    [testFeatures, ] = extractFeatures(img_gray,mser_regions);

    windowedFeatures = single.empty(0,64);

    poi = zeros(size(testRegion));
    numpoints = length(mser_regions);
    n = 1;

    while n <= numpoints
        poi(n) = inpolygon(testRegion(n,1),testRegion(n,2),xv,yv);
        if poi(n) == 1
            windowedFeatures(end+1,:) = testFeatures(n,:);
        end
        n = n+1;
    end
end