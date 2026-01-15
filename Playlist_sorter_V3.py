#This version of the program 

import spotipy
import variables.py
from spotipy.oauth2 import SpotifyOAuth

import sys

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
        self.Owner = None
        self.Playlist_ID = ID
        self.Song_list = None
        self.Length = None

        #Runs the collection of data
        self.Get_playlist_info()
        self.get_songs_in_playlist()
    
    def Get_playlist_info(self):
        """extracts the data for the Playlist(needs to be ran after the creation of the object)"""
        playlist_info = self.sp.playlist(self.Playlist_ID)
        self.Name = playlist_info['name']
        self.Owner = playlist_info['owner']['display_name']
        self.Length = playlist_info['tracks']['total']

    def get_songs_in_playlist(self):
        """Takes the Playlist_ID and Returns a list the of Song objects in a said playlist"""
        # Get the current user's playlists
        playlist = self.sp.playlist(self.Playlist_ID)

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
        
        #audio features
        self.danceability = None
        self.energy = None
        self.loudness = None
        self.speechiness = None
        self.acousticness = None
        self.liveness = None
        self.valence = None

        #Runs the collection of data
        self._Get_Info(track)
        self._Get_Audio_features()

    def _Get_Info(self,track_dict):
        """extracts the data for the Song(needs to be ran after the creation of the object)"""
        self.Name = track_dict['track']['name']
        self.Song_ID = track_dict['track']['uri']

    def _Get_Audio_features(self):
        """Retrives the audio feature data"""

        #retrives the data in the form of a dict
        L = self.sp.audio_features(self.Song_ID)
        D = L[0]

        #sets the vaules
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


def Does_Song_Fit_Genre(PL, genre):
    """Cross references the Stats sheet data to see if a song fits a certain genre,
        takes the playlist and genre as input"""
    D = dict()
    L = []

    with open(f"StatsFolder\{genre}.txt", 'r') as file:
        for line in file.readlines():
            line = line.strip()
            info = line.split(" ")
            feature = info[0].strip("--")
            mean = float(info[1][11:])
            SD = float(info[2][14:])
            D[feature] = [mean, SD]

    threshold_multiplier = 1.5
    attributes = ["danceability", "energy", "loudness", "speechiness", "acousticness", "liveness", "valence"]

    for song in PL.Song_list:
        conditions = all(
            D[attr][0] - threshold_multiplier * D[attr][1] < getattr(song, attr) < D[attr][0] + threshold_multiplier * D[attr][1]
            for attr in attributes
        )

        if conditions:
            L.append(song.Song_ID)

    return L

def MakePlaylist(S,L):
    """Goes through each Key, value pair and makes a PLaylist where the Key is the name of the Playlist and the value becomes the songs in the Playlist"""
    print("starting playlist creation")
    name_of_playlist = input()
    playlist = S.user_playlist_create('vyshnovsky', name_of_playlist, public=False)
    playlist_id = playlist['id']
    if len(L) < 100:
        S.user_playlist_add_tracks('vyshnovsky', playlist_id, L)
    else:
        playlist_length = len(L)
        offset = 0
        Total = 0

        #iterates through all the songs in the playlist 
        while Total <= playlist_length:
            S.playlist_add_items(playlist_id, L[offset:(offset+100)])
            offset += 100
            Total += 100
    print("Playlist made")

def Genre_Picker():
    with open("interface.txt", "r") as file:
        for i in file.readlines():
            print(i)
    num = int(input())
    match num:
        case 0:
            print("Entering the number corresponding to a genre will check your playlist agaisnt a genre")
            return 0
        case 1:
            return "HipHop"
        case 2:
            return "Indie"
        case 3:
            return "R&B"
        case 4:
            return 1 
        case default:
            print("Please Enter a Number or Help")
    return
        
def Main():
    #Authenticte's the User
    S = authenticator()

    #Uses the Playlist ID and makes the Playlist object
    print("Please input the Playlist ID")
    PL_ID = input()
    done = True
    PL = PlayList(S, PL_ID)
    while done:
        Genre = Genre_Picker()
        print(Genre)
        if isinstance(Genre, int) and Genre == 1:
            done = False
            continue
        elif isinstance(Genre, int) and Genre == 0:
            continue
        L = Does_Song_Fit_Genre(PL, Genre)
        MakePlaylist(S,L)

if __name__ == "__main__":
    Main()