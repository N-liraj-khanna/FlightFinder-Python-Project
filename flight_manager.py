import os
import requests

# To get flight details like price and stuff
FLIGHTS_API_KEY = os.environ['FLIGHTS_API_KEY']
FLIGHTS_END_POINT = " http://tequila-api.kiwi.com/v2/search"

# To get list of airports for relevant term
AIRPORT_API_KEY = os.environ['AIRPORT_API_KEY']
AIRPORT_API_SECRET = os.environ['AIRPORT_API_SECRET']
AIRPORT_END_POINT = "https://www.air-port-codes.com/api/v1/multi"


# Manges all the input data and the relevant flights data
class FlightsManager:
    def __init__(self):
        self.user_details = {}
        self.airport_headers = {
            "APC-Auth": AIRPORT_API_KEY,
            "APC-Auth-Secret": AIRPORT_API_SECRET
        }
        self.flights_headers = {
            "apikey": FLIGHTS_API_KEY
        }

    def get_relevant_airports(self, relevant_term):
        params = {
            "term": relevant_term
        }
        airports_response = requests.get(url=AIRPORT_END_POINT,
                                         headers=self.airport_headers, params=params)
        return airports_response.json().get('airports')

    def get_user_flight_details(self, user_requirement_data):
        flights_response = requests.get(url=FLIGHTS_END_POINT, headers=self.flights_headers,
                                        params=user_requirement_data)
        if str(flights_response).split('[')[1].split(']')[0] == '200':
            if flights_response.json()['_results'] != 0:
                return self.return_flight_details(flights_response.json()['data'])
            else:
                return ['0']
        else:
            return ['-1']

    def return_flight_details(self, flights_response):
        all_flights_data = []
        for flight_data in flights_response:
            current_flight_info = ''

            current_flight_info += 'From ' + flight_data['cityFrom']
            current_flight_info += ', ' + flight_data['countryFrom']['name'] + ', ' + flight_data['countryFrom'][
                'code'] + ' \n'
            current_flight_info += 'To ' + flight_data['cityTo'] + ', '
            current_flight_info += flight_data['countryTo']['name'] + ', ' + flight_data['countryTo']['code'] + '.\n'
            current_flight_info += 'Price->\nAdults-> ' + str(flight_data['fare']['adults']) + ' \n'
            current_flight_info += 'Children-> ' + str(flight_data['fare']['children']) + ' \n'
            current_flight_info += 'Infants-> ' + str(flight_data['fare']['infants']) + ' \n'

            current_flight_info += 'Routes ->\n'
            i = 1
            for route in flight_data['route']:
                current_flight_info += 'Route ' + str(i) + ' '
                i += 1
                current_flight_info += 'From ' + route['cityFrom'] + ' city, To '
                current_flight_info += route['cityTo'] + ' city\n'
                current_flight_info += 'Combination ID is ' + route['combination_id'] + ' \n'
                current_flight_info += 'Flight Number -> ' + route['operating_carrier'] + route[
                    'operating_flight_no'] + '\n'
                departure = flight_data['utc_departure'].split('T')
                time = departure[1].split('.')[0]
                current_flight_info += 'On date ' + departure[0] + ' at ' + time + '\n'
            all_flights_data.append(current_flight_info)
        return all_flights_data
