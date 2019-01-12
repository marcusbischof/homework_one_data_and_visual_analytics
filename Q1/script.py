################################################
#
# Marcus Bischof : mbischof6@gatech.edu
# Georgia Institute of Technology
# Data and Visual Analytics
# Homework 1
#
################################################

import http.client
import json
import time
import sys
import collections

# If this program is called as detailed in the HW description: 'python3 script.py <API_KEY>'
# then api_key will contain the appropriate API_KEY from TMDb.
api_key = str(sys.argv[1])
print('api_key --> {}'.format(api_key))

# Establish connection with themoviedb.org
connection = http.client.HTTPSConnection('api.themoviedb.org')

# Meta data for connection.request
headers = {'Content-type': 'application/json'}
genre_request = '/3/genre/movie/list?api_key={}&language=en-US'.format(api_key)

connection.request('GET', genre_request, "", headers)

response = connection.getresponse()

# Contains the entire response, various dramas and their associated IDs. May need later.
genre_list_response = json.loads(response.read().decode())

# Get the id needed for the Drama genre. This will be used to further query this genre.
drama_id = [val['id'] for val in genre_list_response['genres'] if val['name'] == 'Drama'][0]

connection.close()

# The API allows for 40 requests every 10 seconds, structure code (time interval)
# to accomodate this requirement.
