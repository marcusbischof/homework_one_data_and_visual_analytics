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

# Establish connection with themoviedb.org
connection = http.client.HTTPSConnection('api.themoviedb.org')

# Headers & payload for the connection.request(s) that will be called below
headers = {'Content-type': 'application/json'}
payload = ""

genre_request = '/3/genre/movie/list?api_key={}&language=en-US'.format(api_key)
connection.request('GET', genre_request, payload, headers)
response = connection.getresponse()

# Contains the entire response, various dramas and their associated IDs. May need later.
genre_list_response = json.loads(response.read().decode())

# Get the id needed for the Drama genre. This will be used to further query this genre.
drama_id = [val['id'] for val in genre_list_response['genres'] if val['name'] == 'Drama'][0]


################################################
#
# Now that we have the drama ID, we can query against discover such that only movies
# that include this drama are returned by the API call.
#
# API Constraint: Cannot make > 40 requests per 10 seconds.
#
################################################

# Initially 1 since we made a request above to get drama ID
page = contiguous_requests = 1
drama_movies_since_2004_sorted_by_popularity = []

while len(drama_movies_since_2004_sorted_by_popularity) < 350:
    top_350_drama_request='/3/discover/movie?api_key={}&language=en-US&sort_by=popularity.desc&page={}&primary_release_date.gte=2004-01-01&with_genres={}'.format(api_key, page, drama_id)
    page += 1
    contiguous_requests += 1
    connection.request('GET', top_350_drama_request, payload, headers)
    response = connection.getresponse()
    top_350_single_response = json.loads(response.read().decode())
    for resp_obj in top_350_single_response['results']:
        if len(drama_movies_since_2004_sorted_by_popularity) < 350:
            drama_movies_since_2004_sorted_by_popularity.append((resp_obj['id'], resp_obj['original_title']))
        else:
            break
    # Ensures we don't overrequest
    if contiguous_requests == 40:
        sleep(10)
        contiguous_requests=0

connection.close()
