import json
import requests
import pandas as pd

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
    df = pd.DataFrame(response['results'])
    df['elevation'] = df['elevation'].astype(float)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    return df