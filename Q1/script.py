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

# For csv output
import csv

# We will use this to help control the amount of requests (max 10) that we make every ten seconds.
from time import sleep

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

print('Initial genre id request for drama made.')

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

page = 1
movies = []
# Initially 1 since we made a request above to get drama ID
contiguous_requests = 1

print('Beginning to request top 350 drama movies by popularity.')

while len(movies) < 350:
    top_350_drama_request='/3/discover/movie?api_key={}&language=en-US&sort_by=popularity.desc&page={}&primary_release_date.gte=2004-01-01&with_genres={}'.format(api_key, page, drama_id)
    page += 1
    contiguous_requests += 1
    connection.request('GET', top_350_drama_request, payload, headers)
    response = connection.getresponse()
    top_350_single_response = json.loads(response.read().decode())
    for resp_obj in top_350_single_response['results']:
        if len(movies) < 350:
            movies.append((resp_obj['id'], resp_obj['original_title']))
        else:
            break
    if contiguous_requests == 40:
        sleep(10)
        contiguous_requests=0

print('Saving top 350 drama movie IDs.')

# Save values to csv
with open('movie_ID_name.csv', 'w') as f:
    w = csv.DictWriter(f, ['id', 'name'])
    # We do not call w.writeheader() as per homework.
    for row in movies:
        w.writerow({'id' : row[0],'name' : row[1]})

print('Sleeping for 10. Setting clean slate for movie similarity API calls.')

# Let's be safe, ensure fresh API call slate.
sleep(10)

# Dictionary to hold similar IDs per original ID.
similarity_dict = {
    key: [] for key, _ in movies
}

# Iterate through each movie, get similar movies.
contiguous_requests=0

# Used to track API calls made for user display.
api_call_tracker=40

for movie_ID , _ in movies:
    movie_similarity_request = '/3/movie/{}/similar?api_key={}&language=en-US&page=1'.format(movie_ID, api_key)
    connection.request('GET', movie_similarity_request, payload, headers)
    response = connection.getresponse()
    movie_similarity_response = json.loads(response.read().decode())['results']

    # We now add the similar IDs to dict created above.
    if len(movie_similarity_response) >= 5:
        for val in movie_similarity_response[:5]:
            similarity_dict[movie_ID].append(val['id'])
    else:
        for val in movie_similarity_response:
            similarity_dict[movie_ID].append(val['id'])
    contiguous_requests += 1

    # Ensure API threshold not crossed.
    if contiguous_requests == 40:
        print('{} API calls made for movie_similarity, sleep for 10.'.format(api_call_tracker))
        api_call_tracker += 40
        sleep(10)
        contiguous_requests=0

print('Done loading movie similarity data.')

entry_count_before = 0
for k, v in similarity_dict.items():
    entry_count_before += len(v)

print('Length of similarity tuples before dedup --> {}'.format(entry_count_before))

def contains_double_count(key, value, similarity_dict):
    """ Returns true if dict[value] contains key. I.e. double counting. """
    if value in similarity_dict.keys():
        if key in similarity_dict[value]:
            return True
    return False

# Removes double counted IDs.
for k, arr in similarity_dict.items():
    for v in arr:
        if contains_double_count(k, v, similarity_dict):
            for i, v_id in enumerate(similarity_dict[v]):
                if k == v_id:
                    similarity_dict[v].pop(i)

entry_count_after = 0
for k, v in similarity_dict.items():
    entry_count_after += len(v)

print('Length of similarity tuples after dedup --> {}'.format(entry_count_after))

print('Saving similar movies <= 5 for top 350 drama movie IDs.')

# Save values to csv
with open('movie_ID_sim_movie_ID.csv', 'w') as f:
    w = csv.DictWriter(f, ['id', 'sim_id'])
    # We do not call w.writeheader() as per homework.
    for k, val_array in similarity_dict.items():
        for v in val_array:
            w.writerow({'id' : k,'sim_id' : v})

connection.close()
