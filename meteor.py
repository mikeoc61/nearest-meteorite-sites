#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Python3 program which calculates and reports on historical meteor impacts nearest a provided zip code

See: https://www.findlatitudeandlongitude.com/ to identify lat and long for your location

Also see: https://geopy.readthedocs.io/en/stable/ for info on geopy geocoding web services

'''

__author__     = "Michael E. O'Connor"
__copyright__ = "Copyright 2025"

import sys
import math
import requests
from haversine import calc_dist as dist
from geopy.geocoders import Nominatim

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected: {}".format \
    (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()
    
def get_location_details(zip_code):
    # Initialize geolocator with a user-agent
    geolocator = Nominatim(user_agent="zip-code-locator")
    
    # Get the location based on the zip code
    location = geolocator.geocode(zip_code)
    
    # Check if location is found
    if location:
        # Location raw data contains 'address' as a dictionary
        address = location.raw.get('address', {})
        
        # Extract city, state, country with fallbacks
        city = address.get('city', 'N/A') or address.get('town', 'N/A') or address.get('village', 'N/A')
        state = address.get('state', 'N/A')
        country = address.get('country', 'N/A')

        # In case city, state or country are still missing, try using reverse geocoding
        if city == 'N/A' or state == 'N/A' or country == 'N/A':
            # Use reverse geocoding to get more details
            reverse_location = geolocator.reverse(location.point)
            if reverse_location:
                reverse_address = reverse_location.raw.get('address', {})
                city = reverse_address.get('city', city)
                state = reverse_address.get('state', state)
                country = reverse_address.get('country', country)

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
        location_details = get_location_details(zip_code)
        
        if location_details:
            city, state, country, lat, long = location_details
            print(f"City: {city}, State: {state}, Country: {country}")
            print(f"Latitude: {lat}, Longitude: {long}")
        else:
            print("Could not find information for this ZIP code.")
    else:
        print("Invalid ZIP code. Please enter a valid 5-digit ZIP code.")

    print ("Getting impact data from NASA...")
  
    # Get Meteor impact coordinate data from NASA
    meteor_resp = requests.get('https://data.nasa.gov/resource/y77d-th95.json')

    # Convert into JSON format
    meteor_data = meteor_resp.json()

    # Itterate through meteor data and add calculated distance from current location to data set
    # Skip if location coordinates are missing

    print ("Sorting through data, calculating distances...")

    for meteor in meteor_data:
        if not ('reclat' in meteor and 'reclong' in meteor): continue
        meteor['distance'] = dist(float(meteor['reclat']), float(meteor['reclong']), lat, long)
        #print (meteor)

    # Sort meteor data by distance key made arbitrarly large if otherwise missing
    meteor_data.sort(key=get_dist)

    print ("Total meteors in NASA dataset: {0:5d}".format(len(meteor_data)))

    # Print out the 10 closest meteors to land near my location
    for i in range(0,10):
        # print(meteor_data[i])
        print ("#{0:2d} closest meteor was: {1:>7.2f} miles at {2} in {3:.4}".format \
                (i+1, meteor_data[i]['distance'], meteor_data[i]['name'], meteor_data[i]['year']))

# If called from shell as script
if __name__ == '__main__': main()
