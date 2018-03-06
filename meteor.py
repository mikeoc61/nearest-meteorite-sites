#!/usr/bin/env python

'''

Python3 program which calculates and reports on historical meteor impacts nearest our location

See: https://www.findlatitudeandlongitude.com/ to identify lat and long for your location

@author: Michael O'Connor

'''

import math
import requests
from haversine import calc_dist as dist

# Lat and long for Zipcode 75063

my_lat = 32.924702
my_long = -96.959801

# If distance field is missing, populate field with very large number

def get_dist(meteor):
    return meteor.get('distance', math.inf)

if __name__ == '__main__':

    my_loc = (my_lat, my_long)

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
        meteor['distance'] = dist(float(meteor['reclat']), float(meteor['reclong']), my_loc[0], my_loc[1])

    # Sort meteor data by distance key made arbitrarly large if otherwise missing

    meteor_data.sort(key=get_dist)

    # Print out the 10 closest meteors to land near my location

    print ("Total meteors in dataset: {0:6d}".format(len(meteor_data)))

    for i in range(0,10):
        print ("#{0:2d} closest meteor to me is: {1:6.2f} miles in {2:.4}".format(i+1, meteor_data[i]['distance'], meteor_data[i]['year']))
