import populartimes
import doctest
import requests
import json
import itertools
import webbrowser
import folium
import pandas


def get_current_location() -> tuple:
    """ user should enter postal code for regex"""
    pass


def find_closest_stores(current_latitude: float, current_longitude: float) -> list:
    pass


def get_populartimes(key: str, stores: list) -> list:
    """ use set """
    pass


@decorator
def rank_stores(stores: list):
    # make a new dictionary with key values given by algorithm and value of the store
    # for store in stores:


def get_api_key() -> str:
    return 'API KEY'


def generate_map(stores) -> str:
    pass


def print_top_five_stores(stores):
    pass


def get_distance_url(key: str, store: dict, current_position: tuple):
    store_position = store['vicinity']
    return f"https://maps.googleapis.com/maps/api/distancematrix/json?" \
           f"units=imperial&origins={current_position[0]}, {current_position[1]}&destinations={store_position}&key={key}"


def get_distance(key: str, stores: list, current_position: tuple) -> list:
    for store in stores:
        url = get_distance_url(key, store, current_position)
        res = requests.get(url)
        while res.status_code != requests.codes.ok:
            pass
        distance_json = json.loads(res.text)
        store_distance = distance_json['rows']['elements'][0]['distance']['value']  # distance in meters
        store['store_distance'] = store_distance
    return stores


def run():
    key = get_api_key()
    current_latitude, current_longitude = get_current_location()
    stores = find_closest_stores(current_latitude, current_longitude)
    stores = get_populartimes(key, stores)  # ['popular_times'] ['wait_times']
    stores = get_distance(key, stores, (current_latitude, current_longitude))  # ['distance']
    rank_stores(stores)
    print_top_five_stores(stores)
    html_file_name = generate_map(stores)
    webbrowser.open(html_file_name)


def main():
    doctest.testmod()
    run()


if __name__ == '__main__':
    main()