function [ proc_left, proc_right ] = imbalancethresh( image_left, image_right )
%IMBALANCETHRESH uses adaptthresh to mitigate brightness differences
%between left and right pairs due to uneven lighting of the source when
%digitized

    ycbcrleft  = rgb2ycbcr(image_left);
    ycbcrright = rgb2ycbcr(image_right);

    yleft = ycbcrleft(:,:,1);
    yright = ycbcrright(:,:,1);
    yleft = mat2gray(yleft);
    yright = mat2gray(yright);

    yleft = im2double(yleft);
    yright = im2double(yright);

    tleft = adaptthresh(yleft(:,:,1));
    tright = adaptthresh(yright(:,:,1));

    tcleft = imcomplement(tleft);
    tcright = imcomplement(tright);

    testleft = imadd(yleft,0.5*tcleft);
    testright = imadd(yright,0.5*tcright);

    testleft = imadd(yleft,0.5*tright);
    testright = imadd(yright,0.5*tleft);

    testleft = mat2gray(testleft);
    testright = mat2gray(testright);

    testleft = adapthisteq(testleft,'ClipLimit',0.001);
    testright = adapthisteq(testright,'ClipLimit',0.001);
    testset = cat(3,testleft,testright);
    outputset = zeros([size(testleft),2]);

    for n = 1:2
        imtest = testset(:,:,n);
        minfact =  16/255 - min(imtest(:));
        imtest = imtest + minfact;
        maxfact = 240/255 / max(imtest(:));
        imtest = maxfact * imtest;
        imtest = im2uint8(imtest);
        outputset(:,:,n) = imtest;
    end

    outputLeft = ycbcrleft;
    outputLeft(:,:,1) = outputset(:,:,1);
    proc_left = ycbcr2rgb(outputLeft);
    outputRight = ycbcrright;
    outputRight(:,:,1) = outputset(:,:,2);
    proc_right = ycbcr2rgb(outputRight);

end

