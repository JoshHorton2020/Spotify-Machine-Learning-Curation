import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.cluster import KMeans

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='client id',
                                               client_secret='client secret',
                                               redirect_uri='http://localhost:8000',
                                               scope='playlist-read-private playlist-modify-public'))
user_id = sp.current_user()['id']
# Define function to retrieve audio features for a playlist
def get_audio_features(playlist_id):
    results = sp.user_playlist_tracks(user_id, playlist_id=playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_ids = [track['track']['id'] for track in tracks]
    chunks = [track_ids[x:x+100] for x in range(0, len(track_ids), 100)]
    audio_features = []
    for chunk in chunks: 
        audio_features.extend(sp.audio_features(chunk))

    return audio_features

# Retrieve audio features for the original playlist
original_playlist_id = 'styling playlist id'
original_audio_features = get_audio_features(original_playlist_id)

# Store audio features in a pandas dataframe
original_df = pd.DataFrame(original_audio_features)

# Train k-means clustering algorithm on audio features
kmeans = KMeans(n_clusters=5, init='k-means++', random_state=None).fit(original_df.drop(columns=['type', 'id', 'uri', 'track_href', 'analysis_url']))

# Retrieve audio features for the target playlist
target_playlist_id = 'playlist to select songs that match from'
target_audio_features = get_audio_features(target_playlist_id)
target_df = pd.DataFrame(target_audio_features)

# Predict which group each song in the target playlist belongs to
target_df['group'] = kmeans.predict(target_df.drop(columns=['type', 'id', 'uri', 'track_href', 'analysis_url']))

# Get the group of the original playlist
original_group = kmeans.predict(original_df.drop(columns=['type', 'id', 'uri', 'track_href', 'analysis_url']))[0]

# Recommend songs from the target playlist that belong to the same group as the original playlist
recommended_songs = target_df[target_df['group'] == original_group]['uri'].tolist()

name_list = []
for track_id in recommended_songs: 
    track = sp.track(track_id)
    track_name = track['name']
    name_list.append(track_name)
print(name_list)