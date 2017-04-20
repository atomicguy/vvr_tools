function [ thisfigure ] = plotOnImage( image, plot_data, plot_data_2 )
%PLOTONIMAGE displays an image and correlated plot drawn along the lower x
%axis
    
    image_height = size(image,1);
    
    % normalize plot data and flip for display
    plot_data_norm = -plot_data/max(plot_data(:))*image_height/2+image_height;
    
    thisfigure = figure(1);
    imshow(image);
    axis equal;
    hold on
    
%     % wait yellow line
%     plot(plot_data_norm,'Color',[1, 0.82, 0.01],'LineWidth',2);
    
    try
        plot_data_2_norm = -plot_data_2/max(plot_data_2(:))*image_height/2+image_height;
        % pomegranet line
        plot(plot_data_2_norm,'Color',[0.93, 0.27, 0.15],'LineWidth',2);
    catch
        disp('no second plot');
    end
    
    % electric blue line
    plot(plot_data_norm,'Color',[0.02, 0.59, 0.88],'LineWidth',2);
    
    
    hold off

end

