imfred = imread('keystone2.jpg');
fredsize = size(fred);
fred_w = fredsize(2);

sections = 100;

testx = round(fred_w/sections);

filmstrips = {};

n = 1;
j = 0;

while n <= sections
    
    croprect = [j,0,testx,fredsize(1)];
    
    filmstrips{n} = imcrop(imfred, croprect);
    
    j = j + testx;
    n = n+1;
end

entropy_list = {};

m = 1;

while m <= sections
    
    entropy_list{m} = entropy(filmstrips{m});
    
    m = m +1;
end