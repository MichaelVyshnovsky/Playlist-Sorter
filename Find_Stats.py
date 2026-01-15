#This program Takes in a a Spotify Playlist ID/uri and the name of the text file and outputs the mean and standard deviation
#for each of the following feature's:

#danceability
#energy
#loudness
#speechiness
#acousticness
#liveness
#valence

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import numpy as np

class PlayList:
    """
    The Playlsit object stores the 
    sp: the authenticator object
    Name: Name of the Playlist,
    Owner: Who owns the playlist,
    Playlist_ID: The unique code Spotify gives any playlist,
    Song_List: A list of Song Objects
    Length: The total number of songs in the playlist 
    """
    def __init__(self, SP, ID):
        """Sets up the data for the Playlist, sp, Name, Owner, Playlist_ID, Song_list, Length"""
        self.sp = SP
        self.Name = None
        self.Playlist_ID = ID
        self.Song_list = []
        self.Length = None
        self.get_songs_in_playlist()
    
    def get_songs_in_playlist(self):
        """Takes the Playlist_ID and Returns a list the of Song objects in a said playlist"""
        # Get the current user's playlists
        playlist = self.sp.playlist(self.Playlist_ID)


        self.Name = playlist['name']
        self.Length = playlist['tracks']['total']

        # Get the total number of tracks in the playlist
        playlist_length = playlist['tracks']['total']
        
        #Since the Max number of songs you can retrieve from Spotify is 100 you need to requested the song multiple times
        list_of_songs = []
        offset = 0
        limit = 100
        Total = 0

        #iterates through all the songs in the playlist 
        while Total <= playlist_length:

            tracks = self.sp.playlist_tracks(self.Playlist_ID, offset=offset, limit=limit)
            for track in tracks['items']:
                S = Song(self.sp, track)
                list_of_songs.append(S)
            self.Song_list = list_of_songs
            offset += 100
            Total += 100

class Song:
    """
    The Song object stores the 
    sp: the authenticator object
    Name: Name of the Song,
    Artist: Name of the Artist who made the song,
    Song_ID = The unquie Code tht Spotify gives a song
    Artist_Genre = The Genre of the Song's Artist
    """
    def __init__(self, SP, track):
        """Sets up the data for the Song, sp, Name, Artist, Song_ID, Artist_Genre"""
        self.sp = SP
        self.Name = None
        self.Song_ID = None
        
        self.danceability = None
        self.energy = None
        self.loudness = None
        self.speechiness = None
        self.acousticness = None
        self.liveness = None
        self.valence = None

        self._Get_Info(track)
        self._Get_Audio_features()

    def _Get_Info(self,track_dict):
        """extracts the data for the Song"""
        self.Name = track_dict['track']['name']
        self.Song_ID = track_dict['track']['uri']

    def _Get_Audio_features(self):
        """extracts the audio feature's for the Song"""
        L = self.sp.audio_features(self.Song_ID)
        D = L[0]
        print(D)
        self.danceability = D['danceability']
        self.energy = D['energy']
        self.loudness = D['loudness']
        self.speechiness = D['speechiness']
        self.acousticness = D['acousticness']
        self.liveness = D['liveness']
        self.valence = D['valence']

def authenticator():
    """Authenticates the User with the Spotipy API"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = CLIENT_ID,
                                                   client_secret= CLIENT_SECRET,
                                                   redirect_uri= REDIRECT_URI,
                                                   scope= SCOPE))
    return sp

def Write_stats(PL,genre):
    """Takes in the playlist object and genre name then it interates through each song and calculates the mean and std deviation"""

    H = ["danceability", "energy", "loudness", "speechiness", "acousticness", "liveness", "valence"]
    with open(f"StatsFolder\{genre}.txt", 'w') as file:
        for feature in H:
            L = []
            for song in PL.Song_list:
                L.append(getattr(song, feature))
            mean_value = np.mean(L)
            std_deviation = np.std(L)
            file.write(f"{feature}-- mean_value:{mean_value} std_deviation:{std_deviation}\n")

def Main():
    #Authenticte's the User
    S = authenticator()
    print("Authentication complete")
    #Uses the Playlist ID and makes the Playlist object
    print("Please input the Playlist ID")
    PL_ID = input()
    PL = PlayList(S, PL_ID)
    print("Please input the name of the Genre")
    genre = input()
    Write_stats(PL,genre)
    print("Got Stats")

if __name__ == "__main__":
    Main()