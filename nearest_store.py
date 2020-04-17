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
        store['distance'] = store_distance
    return stores


def run():
    key = get_api_key()
    current_latitude, current_longitude = get_current_location()
    stores = find_closest_stores(current_latitude, current_longitude)
    stores = get_populartimes(key, stores)  # ['popular_times'] ['wait_times']
    stores = get_distance(key, stores, (current_latitude, current_longitude))  # ['distance']
    top_five_stores = rank_stores(stores)
    print_top_five_stores(top_five_stores)
    html_file_name = generate_map(top_five_stores)
    webbrowser.open(html_file_name)


def main():
    doctest.testmod()
    run()


if __name__ == '__main__':
    main()
