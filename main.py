from utils import *
import matplotlib
import numpy as np
import plotly.graph_objects as go

'''for processing the data'''
#available locations = 0 - 17
location_id = 1 #JSON with all coordinates has multiple locations (18), pick which one to work with

#tested on 20-100. The bigger it is, the longer it runs
num_splits_for_location = 100 #in how many splits to divide the location (20 = 20x20 grid, 100 = 100x100 grid, etc.)

#tested on 1-5. The bigger it is, the longer it runs
kernel_size = 4 #size of the kernel for the gradient descend (2 = 2x2 kernel, 3 = 3x3 kernel, etc.)

'''for plotting'''
scatter_raise_by = 20 #raise the scatter poits above the surface, for better visibility
scatter_size = 2 #size of the scatter poits
surface_opacity = 0.8 #opacity of the surface itself. 1 is solid, 0 is invisible.
surface_colorscale = 'gray' #default is 'viridis' , other options: https://plotly.com/python/builtin-colorscales/
surface_z_scale = 0.3 #scale the height of the surface. Scaled down due to height and lat/lon (z and x,y) have different units.

if __name__ == '__main__':
    json_path = r'catchments_long.json' #path to JSON file with all coordinates

    #parse JSON to list of coordinates (dictionaries). See function definition for long_json_to_list()
    #extract one dict form the list at id: location_id
    #divide the location into a grid of num_splits_for_location x num_splits_for_location. done by corners_to_grid_by_num_splits()
    #location_grid_by_num_splits: 2 locumns - latitude and longitude, num_splits_for_location^2 rows - coordinates of the grid
    location_grid_by_num_splits = corners_to_grid_by_num_splits(long_json_to_list(json_path)[location_id], num_splits_for_location)

    #call the elevation api of every lat,lon pair in the location_grid_by_num_splits. elevation_api_caller()
    #parse the response to a dataframe. parse_api_resonse_to_dataframe()
    #pivot the dataframe to a grid. pivot()
    pivoted_elevation_grid_by_num_splits = parse_api_resonse_to_dataframe(elevation_api_caller(location_grid_by_num_splits)).pivot(index='latitude', columns='longitude', values='elevation')

    #get a list of 'catchment' dictionaries containing the minima and all points belinging to it.
    catchemnts_dict_list = find_catchments_from_df(df = pivoted_elevation_grid_by_num_splits, radius= kernel_size)

    
    #for plotting local minima
    traces = []

    #plot the surface
    traces.append(go.Surface(z=pivoted_elevation_grid_by_num_splits.transpose().values, 
                            x=pivoted_elevation_grid_by_num_splits.index, 
                            y=pivoted_elevation_grid_by_num_splits.columns,
                            opacity=surface_opacity,
                            colorscale=surface_colorscale,))

    #iterate over each catchemnt, plot the minima and the belonging points
    for i in range(len(catchemnts_dict_list)):
        #random color for the catchment
        color = f'rgb({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)})'

        #mold the data into the formnat plotly wants
        test_group = catchemnts_dict_list[i]
        np_test_group = np.array(test_group['cathcment_points'])
        np_test_group_lats = [pivoted_elevation_grid_by_num_splits.index[item] for item in np_test_group[:,0]]
        np_test_group_lons = [pivoted_elevation_grid_by_num_splits.columns[item] for item in np_test_group[:,1]]
        np_test_group_elevations = [pivoted_elevation_grid_by_num_splits.iloc[item[0], item[1]]+scatter_raise_by for item in np_test_group]

        #plot the points belonging to the minima as circles
        traces.append(go.Scatter3d(x=np_test_group_lats, 
                                y=np_test_group_lons, 
                                z=np_test_group_elevations, 
                                mode='markers', 
                                marker=dict(size=scatter_size, color=color, symbol='circle')))

        #plot the minima as a diamond
        traces.append(go.Scatter3d(x=[pivoted_elevation_grid_by_num_splits.index[test_group['minima'][0]]], 
                                y=[pivoted_elevation_grid_by_num_splits.columns[test_group['minima'][1]]], 
                                z=np.array(pivoted_elevation_grid_by_num_splits.iloc[test_group['minima'][0], test_group['minima'][1]]+scatter_raise_by), 
                                mode='markers', 
                                marker=dict(size=scatter_size + 2, color=color, symbol='diamond')))

    #plot the figure
    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(
            aspectratio=dict(x=1, y=1, z=surface_z_scale),
            aspectmode='manual'
        ), 
        width=1000,
        height=1000
    )

    fig.show()