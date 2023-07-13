import numpy as np
from pandas import json_normalize
from requests import get


def elevation(top_left_lat=None, top_left_lon=None, bottom_right_lat=None, bottom_right_lon=None):
    def get_elevation(lat=None, long=None):
        if lat is None or long is None:
            return None
        query = ('https://api.open-elevation.com/api/v1/lookup'
                 f'?locations={lat},{long}')
        r = get(query, timeout=20)

        if r.status_code == 200 or r.status_code == 201:
            _ele = json_normalize(r.json(), 'results')['elevation'].values[0]
        else:
            _ele = None
        return _ele

    cord = np.mgrid[top_left_lat:bottom_right_lat:.1, top_left_lon:bottom_right_lon:.1]

    shape = (cord.shape[1], cord.shape[2])
    dtype = np.float32
    ele = np.empty(shape, dtype=dtype)
    for i in range(cord.shape[1]):
        for j in range(cord.shape[2]):
            ele[i][j] = get_elevation(lat=cord[0][i][j], long=cord[1][i][j])

    return ele


def road(top_left_lat=None, top_left_lon=None, bottom_right_lat=None, bottom_right_lon=None):
    def get_road_data(lat=None, long=None):
        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={long}'
        response = get(url, timeout=20)
        data = response.json()
        if 'road' in data['address']:
            return True
        else:
            return False

    cord = np.mgrid[top_left_lat:bottom_right_lat:.1, top_left_lon:bottom_right_lon:.1]

    shape = (cord.shape[1], cord.shape[2])
    dtype = np.float32
    is_road = np.empty(shape, dtype=dtype)
    for i in range(cord.shape[1]):
        for j in range(cord.shape[2]):
            is_road[i][j] = get_road_data(lat=cord[0][i][j], long=cord[1][i][j])

    return is_road
