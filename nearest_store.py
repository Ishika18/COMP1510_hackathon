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


def find_closest_stores(current_latitude: float, current_longitude: float) -> dict:
    """
    Find the closest stores from
    :param current_latitude:
    :param current_longitude:
    :return:
    """
    payload = {'location': f'{current_latitude},{current_longitude}',
               'rankby': 'distance',
               'type': 'grocery_or_supermarket',
               'key': get_api_key()}
    data = get_store_results(payload)

    return data


def get_store_results(payload) -> dict:
    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?', params=payload)
    response.raise_for_status()
    data = json.loads(response.text)

    return data['results']


def get_populartimes(stores: list) -> list:
    """ use set """
    pass


def get_score(store: dict):
    wait_time = store['wait_time']  # wait_time key will be appended with populartimes
    distance = store['distance']
    return wait_time / distance


@decorator
def rank_stores(stores: list):
    score_dict = {}
    for store in stores:
        score = get_score(store)
        score_dict[score] = store
    top_scores = sorted(score_dict)
    # SYNTACTIC SUGAR
    return [score_dict[top_scores[i]] for i in range(5)]


def get_api_key() -> str:
    # Do not change this api key unless you have permission
    return 'AIzaSyAVHKBzu0YpNi3o6Y_nYSY_wzNoDTN51mQ'


def generate_map(stores) -> str:
    pass


def print_top_five_stores(stores):
    pass


def get_distance_url(store: dict, current_position: tuple):
    key = get_api_key()
    store_position = store['vicinity']
    return f"https://maps.googleapis.com/maps/api/distancematrix/json?" \
           f"units=imperial&origins={current_position[0]}, {current_position[1]}&destinations={store_position}&key={key}"


def get_distance(stores: list, current_position: tuple) -> list:
    key = get_api_key()
    for store in stores:
        url = get_distance_url(store, current_position)
        res = requests.get(url)
        while res.status_code != requests.codes.ok:
            pass
        distance_json = json.loads(res.text)
        store_distance = distance_json['rows']['elements'][0]['distance']['value']  # distance in meters
        store['distance'] = store_distance
    return stores


def run():
    while True:
        try:
            current_latitude, current_longitude = get_current_location()
        except ValueError as error_message:
            print(error_message)
        else:
            break
    stores = find_closest_stores(current_latitude, current_longitude)
    stores = get_populartimes(stores)  # ['popular_times'] ['wait_times']
    stores = get_distance(stores, (current_latitude, current_longitude))  # ['distance']
    top_five_stores = rank_stores(stores)
    print_top_five_stores(top_five_stores)
    html_file_name = generate_map(top_five_stores)
    webbrowser.open(html_file_name)


def main():
    doctest.testmod()
    run()


if __name__ == '__main__':
    main()
