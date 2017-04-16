function [window_list] = make_growindow(img_dims, start_size, num_steps)
%MAKE_GROWINDOW generates a pair of resizable windows starting on left edge of
%image

    % set generic start_size and step_size to create generic case
    if exist('start_size','var') == 0
        start_size = round(0.1*img_dims(2));
    end
    if exist('step_size','var') == 0
        num_steps = 20;
    end

    img_w = img_dims(2);
    img_h = img_dims(1);
    
    % number of steps determined by initial size and size for both to fill image
    needed_distance = img_w/2 - start_size;
    step_size = floor(needed_distance / num_steps);
    
    window_list = struct('windows',[],'indexPairs',[],'matchmetric',[]);
    
    n = 1;
    k = 0;
    
    while n <= num_steps
        w1 = [0,0,start_size + n * step_size,img_h];
        w2 = [w1(3),0, w1(3), img_h];
        
        window_list(n).windows = [w1,w2];
        
        k = k + 1;
        n = n + 1;
    end

end

