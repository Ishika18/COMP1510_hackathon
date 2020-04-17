from typing import Any

import populartimes
import doctest
import requests
import json
import itertools
import webbrowser
import folium
import pandas
import re


def get_current_location() -> tuple:
    """
    Return the latitude and longitude of the user.

    :return: the latitude as a float and longitude as a float in a tuple
    """
    postal_code = prompt_postal_code()

    key = get_api_key()
    # API USED HERE
    response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address='
                            f'{postal_code}&key={key}')
    response.raise_for_status()
    data = get_coordinate_data(postal_code)
    lat = data['results'][0]['geometry']['location']['lat']
    lon = data['results'][0]['geometry']['location']['lng']
    return lat, lon


def get_coordinate_data(postal_code: str) -> dict:
    """
    Request coordinate data based on user's input postal code.

    :param postal_code: a string
    :return: response data as a dictionary
    """
    key = get_api_key()
    response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address='
                            f'{postal_code}&key={key}')
    response.raise_for_status()
    data = json.loads(response.text)
    if data['status'] == 'ZERO_RESULTS':
        raise ValueError("This location does not exist.")
    else:
        return data


def prompt_postal_code() -> str:
    """
    Prompt the user to enter a postal code.

    :return: a validated postal code as a string
    """
    postal_code = input('Enter a Canadian postal code in the format \'A1A 1A1\': ')
    if validate_postal_code(postal_code):
        return postal_code
    else:
        raise ValueError("Please enter a valid Canadian postal code.")


def validate_postal_code(postal_code: str) -> bool:
    """
    Validate a postal code string.

    :return: True or False
    """
    # REGEX USED HERE
    pattern = re.compile(r'^[A-Z]\d[A-Z] ?\d[A-Z]\d$')
    if pattern.search(postal_code):
        return True
    else:
        return False


def find_closest_stores(current_latitude: float, current_longitude: float) -> list:
    """
    Find the closest stores from response data based on current latitude and longitude
    :param current_latitude: a float
    :param current_longitude: a float
    :return: response data as a list
    """
    payload = {'location': f'{current_latitude},{current_longitude}',
               'rankby': 'distance',
               'type': 'grocery_or_supermarket',
               'key': get_api_key()}
    data = get_store_results(payload)

    return data


def get_store_results(payload) -> list:
    """
    Request store results from Google Places API.

    :param payload: a dictionary of parameter required for the API request
    :return: data results as a dictionary
    """
    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?', params=payload)
    response.raise_for_status()
    data = json.loads(response.text)

    return data['results']


def add_more_data_to_stores(stores: list):
    """ use set """
    key = get_api_key()
    # SET USED HERE
    desired_data = ('international_phone_number', 'current_popularity', 'time_spent')
    for store in stores:
        response = populartimes.get_id(key, store['place_id'])
        for datum in desired_data:
            try:
                store[datum] = response[datum]
            except KeyError:
                # Key error will occur if place does not have data available.
                continue


def get_score(store: dict):
    WAIT_TIME_WEIGHT = 60
    DISTANCE_WEIGHT = 40
    try:
        wait_time = store['time_spent'][0]
        distance = store['distance'] / 1000  # distance in km
        print(wait_time, distance)
        return DISTANCE_WEIGHT / distance + WAIT_TIME_WEIGHT / wait_time
    except KeyError:
        return 0


def write_score(func):
    def wrapper_score(*args, **kwargs):
        top_stores = func(*args, **kwargs)
        for store in top_stores:
            try:
                save_data(
                    f"{store['name']},{store['geometry']['location']['lat']},{store['geometry']['location']['lng']},"
                    f"{store['travel_time']},{store['wait_time']},{store['vicinity'].replace(',', '')}", 'stores.csv')
            except KeyError:
                save_data(
                    f"{store['name']},{store['geometry']['location']['lat']},{store['geometry']['location']['lng']},"
                    f"{store['travel_time']},1000,{store['vicinity'].replace(',', '')}", 'stores.csv')
    return wrapper_score


def save_data(data_to_save: Any, file_name: str) -> None:
    """
    Append the specified input data to the specified file.

    :param data_to_save: an integer
    :param file_name: a string
    :postcondition: correctly appends the input data in the specified file
    """
    with open(file_name, 'a') as results:
        results.write(str(data_to_save) + "\n")


@write_score
def rank_stores(stores: list):
    score_dict = {}
    for store in stores:
        score = get_score(store)
        score_dict[score] = store
    top_scores = sorted(score_dict, reverse=True)
    # SYNTACTIC SUGAR
    return [score_dict[top_scores[i]] for i in range(5)]


def get_api_key() -> str:
    # Do not change this api key unless you have permission
    return 'AIzaSyAJrrx5fu_XACSiqjbvS0LeoF9qzl7NeOc'


def generate_map(stores, lat, lon) -> str:
    # name of the html file
    html_file_name = 'local_map.html'
    icon_size = (50, 35)
    initial_zoom_level = 12

    # initialize map
    local_map = folium.Map(location=[lat, lon], zoom_start=initial_zoom_level)

    # add marker for current location
    folium.CircleMarker(location=(lat, lon), radius=9, tooltip='Current location',
                        color='white', fill_color='#4286F5', fill_opacity=1).add_to(local_map)

    # parse data
    data = pandas.read_csv('stores.csv')
    store_name = list(data['NAME'])
    store_latitude = list(data['LAT'])
    store_longitude = list(data['LON'])
    wait_time = list(data['WAIT'])
    travel_time = list(data['TRAVEL'])

    # add each store as marker
    for i, (name, lat, lon, travel, wait) in enumerate(zip(store_name, store_latitude, store_longitude, travel_time,
                                                           wait_time), 1):
        html_content = """<h1>%s</h1>
        <p>Estimated travel time: %s</p>
        <p>Current wait time: %s</p>
        """
        folium.Marker([lat, lon], popup=html_content % (name, travel, wait), tooltip='Click for more info.',
                      icon=folium.features.CustomIcon(f'{i}.png', icon_size=icon_size)).add_to(local_map)

    # generate html file
    local_map.save(html_file_name)

    return html_file_name


def get_distance_url(store: dict, current_position: tuple):
    key = get_api_key()
    return f"https://maps.googleapis.com/maps/api/distancematrix/json?" \
           f"units=imperial&origins={current_position[0]},{current_position[1]}" \
           f"&destinations={store['geometry']['location']['lat']},{store['geometry']['location']['lng']}&key={key}"


def get_distance(stores: list, current_position: tuple):
    # LIST SLICING
    for store in stores[:]:
        url = get_distance_url(store, current_position)
        print(url)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            raise ConnectionError('error can not reach the server.')
        distance_json = json.loads(res.text)
        print(distance_json)
        store['distance'] = distance_json['rows'][0]['elements'][0]['distance']['value']  # distance in meters
        store['travel_time'] = distance_json['rows'][0]['elements'][0]['duration']['text']  # time in min


def make_score_file(file_name: str):
    with open(file_name, 'w') as results:
        results.write("NAME,LAT,LON,TRAVEL,WAIT,ADDRESS" + "\n")


def run():
    while True:
        try:
            current_latitude, current_longitude = get_current_location()
        except ValueError as error_message:
            print(error_message)
        else:
            break
    make_score_file('stores.csv')
    stores = find_closest_stores(current_latitude, current_longitude)

    add_more_data_to_stores(stores)
    get_distance(stores, (current_latitude, current_longitude))
    top_five_stores = rank_stores(stores)
    html_file_name = generate_map(top_five_stores, current_latitude, current_longitude)
    webbrowser.open(html_file_name)


def main():
    doctest.testmod()
    run()


if __name__ == '__main__':
    main()
