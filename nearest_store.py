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
    pass


def get_api_key() -> str:
    return 'API KEY'


def generate_map(stores) -> str:
    pass


def print_top_five_stores(stores):
    pass


def get_distance(key, stores) -> list:
    pass


def run():
    key = get_api_key()
    current_latitude, current_longitude = get_current_location()
    stores = find_closest_stores(current_latitude, current_longitude)
    stores = get_populartimes(key, stores)  # ['popular_times'] ['wait_times']
    stores = get_distance(key, stores)  # ['distance']
    rank_stores(stores)
    print_top_five_stores(stores)
    html_file_name = generate_map(stores)
    webbrowser.open(html_file_name)


def main():
    doctest.testmod()
    run()


if __name__ == '__main__':
    main()
