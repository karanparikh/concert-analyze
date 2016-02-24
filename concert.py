from sys import argv
from urllib import quote
from requests import get, codes
from operator import itemgetter
import time

# Removed for privacy reasons.
ECHO_NEST_API_KEY = ""

REQUESTS_PER_MIN = 12.0

def get_genres(artist):
  print "Getting genres for " + artist
  base_url = "http://developer.echonest.com/api/v4/artist/profile?api_key=" + \
    ECHO_NEST_API_KEY + \
    "&bucket=genre&format=json&name="
  artist_query_string = quote(artist.strip())
  query_url = base_url + artist_query_string
  res = get(query_url)
  if res.status_code == codes.ok:
    info = res.json()
    genres = info["response"]["artist"]["genres"]
    return genres
  else:
    print "FAILED TO GET GENRES FOR " + artist
    return []

def get_similar_artists(artist):
  print "Getting similar artists for " + artist
  base_url = "http://developer.echonest.com/api/v4/artist/similar?api_key=" + \
    ECHO_NEST_API_KEY + \
    "&format=json&results=5&name="
  artist_query_string = quote(artist.strip())
  query_url = base_url + artist_query_string
  res = get(query_url)
  similar_artists = []
  if res.status_code == codes.ok:
    info = res.json()
    artists = info["response"]["artists"]
    for sim_art in artists:
      similar_artists.append(sim_art["name"])
  else:
    print "FAILED TO GET SIMILAR ARTISTS FOR " + artist
  return similar_artists

def main(artists_file, genres_output_file):
  with open(artists_file) as af:

    similar_freq = dict()
    seen_artists = set()
    
    # Create a file with the genres of all the artists in artists_file.
    with open(genres_output_file, "w+") as gaf:
      for artist in af.readlines():
        seen_artists.add(artist.strip())
        # Crude rate limiting.
        time.sleep(60/REQUESTS_PER_MIN)
        for genre in get_genres(artist):
          genre_name = genre["name"]
          gaf.write(genre_name + "\n")

    # Get the similar artists for each artist I've seen live.
    for artist in seen_artists:
      # Crude rate limiting.
      time.sleep(60/REQUESTS_PER_MIN)
      for similar_artist in get_similar_artists(artist):
        # Only interested in artists I haven't seen yet.
        if not similar_artist in seen_artists:
          if similar_artist in similar_freq:
            similar_freq[similar_artist] = similar_freq[similar_artist] + 1
          else:
            similar_freq[similar_artist] = 1

    # Source: http://stackoverflow.com/a/613218
    similar_freq = sorted(similar_freq.items(), key = itemgetter(1))
    print similar_freq

if __name__ == "__main__":
  # First argument is a file which contains artist names, one per line.
  # Second argument is the name of a file that will contain gneres for each
  # artist in the first line.
  main(argv[1], argv[2])