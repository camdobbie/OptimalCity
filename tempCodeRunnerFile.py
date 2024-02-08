    cmap = colormaps.get_cmap('plasma')
    color_list = [cmap(i/(max(colors)+1)) for i in range(max(colors)+1)]