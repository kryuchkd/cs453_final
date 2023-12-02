import json
import requests
import pandas as pd
import numpy as np

def long_json_to_list(json_path: str) -> list:
    '''Gets a path to a Json file,
    reads it, gets 2 corner coordinates per catchment, returns a list of dicts
    dict format - see below
    catchment_dict = {
            'gauge_id': 0,
            'gauge name': '',
            'lat_1': 0,
            'lon_1': 0,
            'lat_2': 0,
            'lon_2': 0
        }
    '''

    catchment_dict_list = []

    with open(json_path) as f:

        json_obj = json.load(f)

        for feature in json_obj['features'][::3]: #every 3rd record (for some reason , there are 3 copies in a row always)
            curr_dict = {}
            curr_dict['gauge_id'] = feature['properties']['gauge_id']
            curr_dict['gauge name'] = feature['properties']['gauge_name']
            curr_dict['lat_1'] = feature['bbox'][1]
            curr_dict['lon_1'] = feature['bbox'][0]
            curr_dict['lat_2'] = feature['bbox'][3]
            curr_dict['lon_2'] = feature['bbox'][2]

            catchment_dict_list.append(curr_dict)
        
    return catchment_dict_list

def elevation_api_caller(locations: list) -> dict:
    '''
    api doc: https://github.com/Jorl17/open-elevation/blob/master/docs/api.md
    gets a list of location tuples : [(lat, lon), (lat, lon), ...]
    calls the api with all of them at once (see api doc)
    returns a dict with the response (for format also see api doc)
    '''
    url = "https://api.open-elevation.com/api/v1/lookup"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Prepare the request payload
    payload = {
        "locations": [
            {"latitude": lat, "longitude": lon} for lat, lon in locations
        ]
    }

    # Make the API call
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        return None

def corners_to_grid_by_num_splits(catchment: dict, num_splits: int) -> list:
    '''
    gets a catchment dict (see long_json_to_list)
    and a number of splits (int)
    creates a grid of num_splits^2 points inside the coodinate corners
    just devides the space into num_splits * num_splits points
    returns a list of tuples (lat, lon) of the grid
    '''
    lat_1 = catchment['lat_1']
    lon_1 = catchment['lon_1']
    lat_2 = catchment['lat_2']
    lon_2 = catchment['lon_2']

    larger_lat = max(lat_1, lat_2)
    smaller_lat = min(lat_1, lat_2)
    larger_lon = max(lon_1, lon_2)
    smaller_lon = min(lon_1, lon_2)

    lat_step_size = (larger_lat - smaller_lat) / num_splits
    lon_step_size = (larger_lon - smaller_lon) / num_splits

    grid = []
    for i in range(num_splits):
        for j in range(num_splits):
            grid.append((smaller_lat + i * lat_step_size, smaller_lon + j * lon_step_size))
    
    return grid

def corners_to_grid_by_step_size(catchment: dict, step_size: float) -> list:
    '''
    gets a catchment dict (see long_json_to_list)
    and a step size (float)
    creates a grid of points inside the coodinate corners
    just same as the other function, just gives you an option to provide a step size in degrees
    returns a list of tuples (lat, lon) of the grid
    '''
    lat_1 = catchment['lat_1']
    lon_1 = catchment['lon_1']
    lat_2 = catchment['lat_2']
    lon_2 = catchment['lon_2']

    larger_lat = max(lat_1, lat_2)
    smaller_lat = min(lat_1, lat_2)
    larger_lon = max(lon_1, lon_2)
    smaller_lon = min(lon_1, lon_2)

    lat_step_size = step_size
    lon_step_size = step_size

    grid = []
    for i in range(int((larger_lat - smaller_lat) / lat_step_size)):
        for j in range(int((larger_lon - smaller_lon) / lon_step_size)):
            grid.append((smaller_lat + i * lat_step_size, smaller_lon + j * lon_step_size))
    
    return grid

def parse_api_resonse_to_dataframe(response: dict) -> pd.DataFrame:
    '''
    gets a response from the api (see elevation_api_caller)
    which is a dictionary
    parses it into a dataframe
    (hint: dictionary one field: 'results' which is a list of dictionaries with keys 'latitude', 'longitude', 'elevation')
    returns a dataframe with columns 'latitude', 'longitude', 'elevation'
    '''
    df = pd.DataFrame(response['results'])
    df['elevation'] = df['elevation'].astype(float)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    return df
'''
def find_minima_for_point(lat_idx: int, lon_idx: int, radius: int, df: pd.DataFrame) -> tuple:
    df_as_np_array = df.to_numpy()
    curr_lat = lat_idx
    curr_lon = lon_idx

    while True:
        new_near_lowest_lat, new_near_lowest_lon = min_around_point(curr_lat, curr_lon, radius, df_as_np_array)
        if new_near_lowest_lat == curr_lat and new_near_lowest_lon == curr_lon:
            break
        curr_lat = new_near_lowest_lat
        curr_lon = new_near_lowest_lon
    
    return (curr_lat, curr_lon)


def generate_tuples_around_point(x, y, radius):
    result = []
    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            result.append((i, j))
    return result

def min_around_point(lat_idx: int, lon_idx: int, radius: int, np_arr: np.array) -> tuple:
    curr_lowest = np_arr[lat_idx, lon_idx]
    curr_lowest_lat = lat_idx
    curr_lowest_lon = lon_idx
    for lat, lon in generate_tuples_around_point(lat_idx, lon_idx, radius):
        if lat == lat_idx and lon == lon_idx:
            continue
        if lat < 0 or lon < 0 or lat >= np_arr.shape[0] or lon >= np_arr.shape[1]:
            continue
        if np_arr[lat, lon] < curr_lowest:
            curr_lowest = np_arr[lat, lon]
            curr_lowest_lat = lat
            curr_lowest_lon = lon
    return (curr_lowest_lat, curr_lowest_lon)
'''

def find_minima_for_point(lat_idx: int, lon_idx: int, radius: int, df: pd.DataFrame) -> tuple:
    
    curr_lat = lat_idx
    curr_lon = lon_idx

    while True:
        new_near_lowest_lat, new_near_lowest_lon = min_around_point(curr_lat, curr_lon, radius, df)
        if new_near_lowest_lat == curr_lat and new_near_lowest_lon == curr_lon:
            break
        curr_lat = new_near_lowest_lat
        curr_lon = new_near_lowest_lon
    
    return (curr_lat, curr_lon)


def generate_tuples_around_point(x, y, radius):
    result = []
    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            result.append((i, j))
    return result

def min_around_point(lat_idx: int, lon_idx: int, radius: int, df: pd.DataFrame) -> tuple:
    curr_lowest = df.iloc[lat_idx, lon_idx]
    curr_lowest_lat = lat_idx
    curr_lowest_lon = lon_idx
    for lat, lon in generate_tuples_around_point(lat_idx, lon_idx, radius):
        if lat == lat_idx and lon == lon_idx:
            continue
        if lat < 0 or lon < 0 or lat >= df.shape[0] or lon >= df.shape[1]:
            continue
        if df.iloc[lat, lon] < curr_lowest:
            curr_lowest = df.iloc[lat, lon]
            curr_lowest_lat = lat
            curr_lowest_lon = lon
    return (curr_lowest_lat, curr_lowest_lon)

def find_catchments_from_df(df: pd.DataFrame, radius: int) -> list:
    '''
    catchment = {
        'minima': (lat, lon),
        'cathcment_points': [(lat, lon), (lat, lon), ...]
    }

    returns a list of catchments
    '''
    grid_size = df.shape[0] # assuming square grid
    start_to_dest_dict_list = [] # list of dicts with keys: 'start_lat', 'start_lon', 'dest_lat', 'dest_lon'. for every point we save it's lat, lon and the lat, lon of the minima it descends to
    minimas = [] # list of tuples (lat, lon) of the minimas
    catchment_dict_list = [] # list of catchments

    for i in range(grid_size):
        for j in range(grid_size):
            (dest_lat, dest_lon) = find_minima_for_point(lat_idx= i, lon_idx= j, radius= radius, df=df) # find the minima for the current point
            result = {'start_lat': i, 'start_lon': j, 'dest_lat': dest_lat, 'dest_lon': dest_lon} # create a dict for the current point and the minima it descends to
            start_to_dest_dict_list.append(result) # add the dict to the list
            
            if i == dest_lat and j == dest_lon: # if the current point is a minima (descends to itself)
                minimas.append((i, j)) # add it to the minimas list
            
            found_a_slot = False
            for item in catchment_dict_list:
                if item['minima'] == (dest_lat, dest_lon):
                    item['cathcment_points'].append((i, j))
                    found_a_slot = True
                    break
            if not found_a_slot:
                catchment_dict_list.append({'minima': (dest_lat, dest_lon), 'cathcment_points': [(i, j)]})
    
    return catchment_dict_list
    

    