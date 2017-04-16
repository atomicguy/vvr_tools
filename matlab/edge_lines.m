clear;clc;

image = imread('G91F174_067F.tiff');

imshow(image);

image_size = size(image);
image_width = image_size(2);

image_edges = rangefilt(image);
image_edges_gray = rgb2gray(image_edges);
image_edges_boosted = adapthisteq(image_edges_gray);

image_accum = zeros(5,image_width);

n = 1;
while n <= image_width
    image_accum(1,n) = sum(image_edges_gray(:,n));
    image_accum(2,n) = median(image_edges_gray(:,n));
    image_accum(3,n) = entropy(image_edges_gray(:,n));
    image_accum(4,n) = std(double(image_edges_gray(:,n)));
    image_accum(5,n) = mean(image_edges_gray(:,n));
    
    n = n+1;
end

%%

figure, 
subplot(2,1,1);
imshow(image_edges_boosted);

subplot(2,1,2);
hold on;
% plot(image_accum(5,:),'Color','r');
plot(image_accum(2,:),'Color','g');
plot(y);
% plot(image_accum(3,:),'Color','b');
