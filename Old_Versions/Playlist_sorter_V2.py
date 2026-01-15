import spotipy
from spotipy.oauth2 import SpotifyOAuth

import networkx as nx
from networkx.algorithms import community

import os, multiprocessing, math

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
    def __init__(self, SP, ID,):
        """Sets up the data for the Playlist, sp, Name, Owner, Playlist_ID, Song_list, Length"""
        self.sp = SP
        self.Name = None
        self.Owner = None
        self.Playlist_ID = ID
        self.Song_list = []
        self.Length = None
        self.Get_playlist_info()
        self.get_songs_in_playlist()

    
    def Get_playlist_info(self):
        """extracts the data for the Playlist(needs to be ran after the creation of the object)"""
        playlist_info = self.sp.playlist(self.Playlist_ID)
        self.Name = playlist_info['name']
        self.Owner = playlist_info['owner']['display_name']
        self.Length = playlist_info['tracks']['total']

    def Thread_Function(self, num_of_songs, offset):
        Total = 0
        limit = num_of_songs

        while Total < num_of_songs:
            tracks = self.sp.playlist_tracks(self.Playlist_ID, offset=offset, limit=limit)
            for track in tracks['items']:
                S = Song(self.sp, track)
                self.Song_list.append(S)
            Total += num_of_songs


    def get_songs_in_playlist(self):
        """Takes the Playlist_ID and Returns a list the of Song objects in a said playlist"""
        # Get the current user's playlists
        playlist = self.sp.playlist(self.Playlist_ID)

        # Get the total number of tracks in the playlist
        playlist_length = playlist['tracks']['total']
        
        #Since the Max number of songs you can retrieve from Spotify is 100 you need to requested the song multiple times

        num_threads = os.cpu_count()
        
        songs_per_thread = math.ceil(self.Length / num_threads)
        
        for i in range(num_threads):
            # Create two threads
            
            thread = multiprocessing.Process(target=self.Thread_Function(songs_per_thread, i * songs_per_thread))

            # Start the threads
            print(f'starting thread {i}')
            thread.start()

            # Wait for threads to finish
            thread.join()
        print('All thread done')
        self.Song_list

        

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
        self.Artist = None
        self.Name = None
        self.Song_ID = None
        self.Artist_Genre = None
        self._Get_Info(track)
        self._Get_artist_genre()

    def _Get_Info(self,track_dict):
        """extracts the data for the Song(needs to be ran after the creation of the object)"""
        self.Artist = track_dict['track']['artists'][0]['name']
        self.Name = track_dict['track']['name']
        self.Song_ID = track_dict['track']['uri']

    def _Get_artist_genre(self):
        """Takes in an Artist name as input and returns the Main Genre of that artist"""
        results = self.sp.search(q='artist:' + self.Artist, type='artist')
        if results['artists']['items']:
            artist_info = self.sp.artist(results['artists']['items'][0]['id'])
            self.Artist_Genre = artist_info['genres']

def authenticator():
    """Authenticates the User with the Spotipy API"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = CLIENT_ID,
                                                   client_secret= CLIENT_SECRET,
                                                   redirect_uri= REDIRECT_URI,
                                                   scope= SCOPE))
    return sp


def group_similar_genres(list_of_songs):
    """
    This function groups similar musical genres by creating a genre graph based on co-occurrences in artists, 
    applying a community detection algorithm to group the genres.
    
    Returns:
    list: A list of sets, where each set contains the genres in a community
    """
    try:
        # Connect to Spotify's catalog and retrieve the tags for each musical genre
        # (code for this step is not provided as it is outside the scope of this function)
        artists = []
        for i in list_of_songs:
            artists.append(i.Artist_Genre)

        # Create a graph where each node represents a genre and edges represent co-occurrences in artists
        genre_graph = nx.Graph()
        for artist in artists:
            genres = artist
            for i in range(len(genres)):
                for j in range(i+1, len(genres)):
                    if genre_graph.has_edge(genres[i], genres[j]):
                        genre_graph[genres[i]][genres[j]]['weight'] += 1
                    else:
                        genre_graph.add_edge(genres[i], genres[j], weight=1)
        
        # Apply a community detection algorithm to group the genres
        communities = community.greedy_modularity_communities(genre_graph)
        
        # Return the list of genre communities
        return [set(c) for c in communities]
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        return []
    
def Make_SubPlaylist_Dict(PL,artist_communities):
    """Makes a Dict whre the Key is 'Playlist: k' and the value is a list of related Genre's"""
    #Makes the Dict
    D = {}
    #This first loop makes One Playlist for any Songs with no Artist Genre
    D['Playlist: 0'] = set()
    for i in PL.Song_list:
        if not i.Artist_Genre:
            D['Playlist: 0'].add(i.Song_ID)

    #The other loops goes through each Genre communities and makes a list of songs
    for k, set_of_genre in enumerate(artist_communities):
        Name = f"PlayList: {k+1}"
        D[Name] = set() 
        for genre in set_of_genre:
            for i in PL.Song_list:
                for j in i.Artist_Genre:
                    if genre == j:
                        D[Name].add(i.Song_ID)
    return D

def MakePlaylist(S,D):
    """Goes through each Key, value pair and makes a PLaylist where the Key is the name of the Playlist and the value becomes the songs in the Playlist"""
    for i in D:
        playlist = S.user_playlist_create('vyshnovsky', i, public=False)
        playlist_id = playlist['id']
        tracks_to_add = []

        for p in list(D[i]):
            tracks_to_add.append(p)
        S.user_playlist_add_tracks('vyshnovsky', playlist_id, tracks_to_add)
        print(f"playlist made: {i}")

def Main():
    #Authenticte's the User
    S = authenticator()

    #Uses the Playlist ID and makes the Playlist object
    PL_ID = '2jf1AwtUtN2avwQAt3dsBo'
    PL = PlayList(S, PL_ID)
    #makes the Genre Communities 
    Genre_Communities = group_similar_genres(PL.Song_list)

    #Makes the Playlist
    D = Make_SubPlaylist_Dict(PL,Genre_Communities)
    MakePlaylist(S,D)


if __name__ == "__main__":
    Main()