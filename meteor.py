#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Python3 program which calculates and reports on historical meteor impacts nearest our location

See: https://www.findlatitudeandlongitude.com/ to identify lat and long for your location

'''

_author__     = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

import sys
import math
import requests
from haversine import calc_dist as dist
from geopy.geocoders import Nominatim

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected: {}".format \
    (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()

# Lat and long for Zipcode 75063

# my_lat = 32.924702
# my_long = -96.959801

def get_lat_long(zip_code):
    # Initialize geolocator with a user-agent
    geolocator = Nominatim(user_agent="zip-code-locator")
    
    # Get the location based on the zip code
    location = geolocator.geocode(zip_code)
    
    # Check if location is found
    if location:
        return location.latitude, location.longitude
    else:
        return None
    
def get_location_details(zip_code):
    # Initialize geolocator with a user-agent
    geolocator = Nominatim(user_agent="zip-code-locator")
    
    # Get the location based on the zip code
    location = geolocator.geocode(zip_code)
    
    # Check if location is found
    if location:
        # Location object contains city, state, country, and coordinates
        city = location.raw.get('address', {}).get('city', 'N/A')
        state = location.raw.get('address', {}).get('state', 'N/A')
        country = location.raw.get('address', {}).get('country', 'N/A')
        return city, state, country, location.latitude, location.longitude
    else:
        return None

# If distance field is missing, populate field with very large number

def get_dist(meteor):
    return meteor.get('distance', math.inf)

def main():

    # Prompt the user for a 5-digit zip code

    zip_code = input("Please enter a 5-digit ZIP code: ")

    # Validate that the zip code is 5 digits

    if len(zip_code) == 5 and zip_code.isdigit():
        # coordinates = get_lat_long(zip_code)
        location_details = get_location_details(zip_code)
        
        if location_details:
            city, state, country, my_lat, my_long = location_details
            print(f"City: {city}, State: {state}, Country: {country}")
            print(f"Latitude: {my_lat}, Longitude: {my_long}")

            print(f"Raw: {location_details}")
        else:
            print("Could not find information for this ZIP code.")

    else:
        print("Invalid ZIP code. Please enter a valid 5-digit ZIP code.")

    # Get Meteor impact coordinate data from NASA

    print ("Getting impact data from NASA...")

    meteor_resp = requests.get('https://data.nasa.gov/resource/y77d-th95.json')

    # Convert into JSON format

    meteor_data = meteor_resp.json()

    # Itterate through meteor data and add calculated distance from current location to data set
    # Skip if location coordinates are missing

    print ("Sorting through data, calculating distances...")

    for meteor in meteor_data:
        if not ('reclat' in meteor and 'reclong' in meteor): continue
        meteor['distance'] = dist(float(meteor['reclat']), float(meteor['reclong']), my_lat, my_long)
        #print (meteor)

    # Sort meteor data by distance key made arbitrarly large if otherwise missing

    meteor_data.sort(key=get_dist)

    print ("Total meteors in NASA dataset: {0:5d}".format(len(meteor_data)))

    # Print out the 10 closest meteors to land near my location

    for i in range(0,10):
        print ("#{0:2d} closest meteor to me is: {1:6.2f} miles in {2:.4}".format \
                (i+1, meteor_data[i]['distance'], meteor_data[i]['year']))

# If called from shell as script

if __name__ == '__main__': main()
