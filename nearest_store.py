from typing import Any, Callable, Tuple, Dict

import populartimes
import doctest
import requests
import json
import webbrowser
import folium
import pandas
import re
import itertools
import sys


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
    if response.status_code != requests.codes.ok:
        raise ConnectionError("Server cannot be reached")
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
    if response.status_code != requests.codes.ok:
        raise ConnectionError("Server cannot be reached")
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
    Validate a postal code string non-case sensitive.

    :return: True or False

    >>> validate_postal_code('111 111')
    False
    >>> validate_postal_code('XXX XXX')
    False
    >>> validate_postal_code('1X1 X1X')
    False
    >>> validate_postal_code('A1A 1A1')
    True
    >>> validate_postal_code('a1a 1a1')
    True
    >>> validate_postal_code('A1A1A1')
    True
    """
    # REGEX USED HERE
    pattern = re.compile(r'^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$')

    return True if pattern.search(postal_code) else False


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
               'opennow': 'True',
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
    if response.status_code != requests.codes.ok:
        raise ConnectionError("Server cannot be reached")
    data = json.loads(response.text)

    return data['results']


def add_more_data_to_stores(stores: list):
    """
    Add more information in the existing list of stores.

    :param stores: a list of dictionaries representing stores from Google Places API
    :precondition: stores should be a correctly formatted list of dictionaries
    :postcondition: add new key value to stores in existing list
    """
    key = get_api_key()
    # SET USED HERE
    desired_data = {'international_phone_number', 'current_popularity', 'time_spent'}
    for store in stores:
        response = populartimes.get_id(key, store['place_id'])
        for datum in desired_data:
            try:
                store[datum] = response[datum]
            except KeyError:
                # Key error will occur if place does not have data available. We will skip the data.
                continue


def get_score(store: dict) -> float:
    """
    Get the score of specified store using decision making algorithm.

    :param store: a dictionary
    :precondition: input parameter store must be a well formed dictionary representing the store
    :postcondition: correctly returns the score value of the score
    :return: a float
    """
    SECONDS = 60
    WAIT_TIME_WEIGHT = 50  # lower wait time is weighted higher
    POPULAR_WEIGHT = 50
    TRAVEL_WEIGHT = 10  # travel time is weighted lower because driving is better than waiting

    try:
        wait_time = store['time_spent'][0]
        travel_time = store['time_value'] / SECONDS
        store_popularity = store['current_popularity']
        return TRAVEL_WEIGHT / travel_time + WAIT_TIME_WEIGHT / wait_time + POPULAR_WEIGHT / store_popularity

    except KeyError:
        return 0


def write_score(func: Callable[[Any, Any], Any]) -> (Tuple[Any, ...], Dict[str, Any]):
    """
    Save the store data of the decorated function in a file.

    :param func: a function
    :return: a function
    """

    def wrapper_score(*args, **kwargs):
        top_stores = func(*args, **kwargs)
        for store in top_stores:
            try:
                save_data(
                    f"{store['name']},{store['geometry']['location']['lat']},{store['geometry']['location']['lng']},"
                    f"{store['travel_time']},{store['time_spent'][0]} mins,"
                    f"{store['vicinity'].replace(',', '')},{store['current_popularity']}", 'stores.csv')
            except KeyError:
                pass
    return wrapper_score


def save_data(data_to_save: Any, file_name: str):
    """
    Append the specified input data to the specified file.

    :param data_to_save: an integer
    :param file_name: a string
    :precondition: file_name must be a string
    :postcondition: correctly appends the input data in the specified file
    """
    with open(file_name, 'a') as results:
        results.write(str(data_to_save) + "\n")


# FUNCTION DECORATOR
@write_score
def rank_stores(stores: list) -> list:
    """
    Return the list of the top stores (at most 5).

    :param stores: a list of dictionaries representing stores
    :precondition: input parameter stores must a correctly formatted stores
    :postcondition: correctly returns the top stores (according to their scores)
    :return: a list of stores
    """
    CUTOFF = 5
    score_dict = {}
    for store in stores:
        score = get_score(store)
        score_dict[score] = store
    top_scores = sorted(score_dict, reverse=True)
    # LIST COMPREHENSION AND RANGE AND ITERTOOLS
    try:
        return [score_dict[top_scores[i]] for i in range(CUTOFF)]
    except IndexError:
        return [score_dict[top_scores[i]] for i in range(len(top_scores))]


def get_api_key() -> str:
    """
    Return the api key constant.

    :return: an api key as a string
    """
    # Do not change this api key unless you have permission
    return 'AIzaSyBw6AIHV6RIhH4b_Z-2iJI_LX5GGJIt7zI'


def parse_data(file_name: str) -> dict:
    """
    Return the store attributes of the stores in the specified file name.

    :param file_name: a string, representing the file name containing stores information
    :return: a dictionary of store attributes
    """
    data = pandas.read_csv(file_name)
    store_attribute_keys = ['store_name', 'store_latitude', 'store_longitude', 'travel_time', 'wait_time',
                            'store_address', 'store_popularity']
    store_attribute_values = [list(data['NAME']), list(data['LAT']), list(data['LON']), list(data['TRAVEL']),
                              list(data['WAIT']), list(data['ADDRESS']), list(data['POPULARITY'])]
    # DICTIONARY COMPREHENSION
    store_attributes = {key: value for key, value in zip(store_attribute_keys, store_attribute_values)}
    return store_attributes


def generate_map(file_name: str, lat: float, lon: float) -> str:
    """
    Return the html file name with appended html elements inside the file.

    :param file_name: a string representing the valid file name
    :param lat: a float
    :param lon: a float
    :return: a string, representing the html file name
    """
    # name of the html file
    html_file_name = 'local_map.html'
    icon_size = (50, 35)
    initial_zoom_level = 12
    marker_radius = 9

    # initialize map
    local_map = folium.Map(location=[lat, lon], zoom_start=initial_zoom_level)

    # add marker for current location
    folium.CircleMarker(location=(lat, lon), radius=marker_radius, tooltip='Current location',
                        color='white', fill_color='#4286F5', fill_opacity=1).add_to(local_map)

    # parse data
    store_attributes = parse_data(file_name)

    # add each store as marker
    store_amount = len(store_attributes['store_name'])
    # USED ITERTOOLS MODULE HERE
    for i in itertools.islice(itertools.count(), store_amount):
        html_content = """<h1>%s</h1>
        <p>Estimated travel time: %s</p>
        <p>Current wait time: %s</p>
        <p>Address: %s</p>
        <p>Crowdedness: %s%%</p>
        """
        folium.Marker([store_attributes['store_latitude'][i], store_attributes['store_longitude'][i]],
                      popup=html_content % (store_attributes['store_name'][i], store_attributes['travel_time'][i],
                                            store_attributes['wait_time'][i], store_attributes['store_address'][i],
                                            store_attributes['store_popularity'][i]),
                      tooltip='Click for more info.',
                      icon=folium.features.CustomIcon(f'{i+1}.png', icon_size=icon_size)).add_to(local_map)

    # generate html file
    local_map.save(html_file_name)

    return html_file_name


def get_distance_url(store: dict, current_position: tuple):
    """
    Return the url for distance matrix api.

    :param store: a dictionary of stores
    :param current_position: a tuple, representing the current location
    :return: a string, representing the url
    """
    key = get_api_key()
    return f"https://maps.googleapis.com/maps/api/distancematrix/json?" \
           f"units=imperial&origins={current_position[0]},{current_position[1]}" \
           f"&destinations={store['geometry']['location']['lat']},{store['geometry']['location']['lng']}&key={key}"


def get_distance(stores: list, current_position: tuple):
    """
    Add distance, travel_time and time_value to the stores in the stores dictionary.

    :param stores: a list of dictionaries representing the stores
    :param current_position: a tuple, representing the current position
    :precondition: stores must be a correctly formatted list of store dictionaries
    :postcondition: correctly adds the distance, travel_time and time_value to the store dictionaries in the given list
    """
    # LIST SLICING
    for store in stores[:]:
        url = get_distance_url(store, current_position)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            raise ConnectionError('error can not reach the server.')
        distance_json = json.loads(res.text)
        store['distance'] = distance_json['rows'][0]['elements'][0]['distance']['value']  # distance in meters
        store['travel_time'] = distance_json['rows'][0]['elements'][0]['duration']['text']  # time in min
        store['time_value'] = distance_json['rows'][0]['elements'][0]['duration']['value']


def make_score_file() -> str:
    """
    Return the file name to store the stores data.

    :return: a string
    """
    FILE_NAME = 'stores.csv'
    with open(FILE_NAME, 'w') as results:
        results.write("NAME,LAT,LON,TRAVEL,WAIT,ADDRESS,POPULARITY" + "\n")

    return FILE_NAME


def print_stores(file_name: str):
    """
    Print the stores information in a user friendly manner.

    :param file_name: a string, representing the file name containing stores information
    :precondition: input parameter file_name must be a string representing valid file name
    :postcondition: correctly prints the information of the stores
    """
    store_data = parse_data(file_name)
    store_amount = len(store_data['store_name'])
    print("---------------------------------")
    if store_amount == 0:
        print("There are no stores open near you.")
    else:
        # USED ENUMERATE HERE AND FORMATTED OUTPUTS
        for i, store in enumerate(range(store_amount), 1):
            print("%d. %s " % (i, store_data['store_name'][store]))
            print("Travel Time: %s" % (store_data['travel_time'][store]))
            print("Crowdedness: %s" % (store_data['store_popularity'][store]))
            print("Wait Time: %s" % (store_data['wait_time'][store]))
            print("---------------------------------")


def run():
    """
    Run the functions.
    """
    # USED TRY FINALLY HERE
    user_input = None
    file_name = make_score_file()
    while user_input != 'q':
        try:
            current_latitude, current_longitude = get_current_location()
            stores = find_closest_stores(current_latitude, current_longitude)
            add_more_data_to_stores(stores)
            get_distance(stores, (current_latitude, current_longitude))
            rank_stores(stores)
            print_stores(file_name)
            html_file_name = generate_map(file_name, current_latitude, current_longitude)
            platform = sys.platform
            if platform == 'win32':
                webbrowser.open(html_file_name)
            else:
                webbrowser.get('open -a /Applications/Google\ Chrome.app %s').open(html_file_name)
        except (ConnectionError, ValueError, IndexError) as error_message:
            print(error_message)
        finally:
            user_input = input("Enter 'q' to quit, enter anything else to try again: ").strip().lower()


def main():
    """
    Run the program.
    """
    doctest.testmod()
    run()


if __name__ == '__main__':
    main()
