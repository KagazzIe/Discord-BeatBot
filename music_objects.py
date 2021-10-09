from collections import deque
import discord
import youtube_dl
from music_objects import *
from threading import Lock

# YTDL options https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312
ytdl_search = youtube_dl.YoutubeDL({'format': 'bestaudio/best',
                                    'noplaylist': True,
                                    'default_search': 'auto',
                                    'quiet':False}
                                   )
ytdl_metadata_search = youtube_dl.YoutubeDL({'format': 'bestaudio/best',
                                    'noplaylist': True,
                                    'default_search': 'auto',
                                    'skip_download':True,
                                    'simulate':True,
                                    'quiet':False}
                                   )

ytdl_link = youtube_dl.YoutubeDL({
                                'format': 'bestaudio/best',
                                'noplaylist': True,
                                'quiet':False}
                                 )
ytdl_metadata_link = youtube_dl.YoutubeDL({
                                'format': 'bestaudio/best',
                                'noplaylist': True,
                                'skip_download':True,
                                'simulate':True,
                                'quiet':False}
                                 )

ytdl_metadata_playlist = youtube_dl.YoutubeDL({
                                'format': 'bestaudio/best',
                                'noplaylist': False,
                                'playliststart':1,
                                'playlistend':1,
                                'skip_download':True,
                                'simulate':True,
                                'quiet':False}
                                 )


ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

class Song(discord.PCMVolumeTransformer):
    def __init__(self, search_term=None, data=None):
        self.search_term = search_term
        self._data = data
        self._title = None
        self._url = None
        self.fucked = False
        if data:
            super().__init__(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options))
            self._title = data.get('title')
            self._url = data.get('url')
        
    
    def search(self):
        try:
            data = ytdl_search.extract_info('ytsearch:{%s}' % (self.search_term), download=False)['entries'][0]
        except:
            self.fucked = True
            return False
        self._data = data
        return data
    
    def fetch_link(self):
        try:
            data = ytdl_link.extract_info(self.search_term, download=False)
        except:
            self.fucked = True
            return False
        self._data = data
        return data

    def download(self):
        """
        Will downlod the song.
        Will also get the title and url
        """
        print('Downloading Song')
        if 'https://www.youtube.com/watch?v=' in self.search_term:
            data = self.fetch_link()
        else:
            data = self.search()
        if data: 
            self._title = data.get('title')
            self._url = data.get('url')
            super().__init__(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options))
            return True
        else:
            return False

    def download_metadata(self):
        """
        Will download the metadata for the song
        If the metadata is already downloaded, then return
        """
        if self._title and self._url:
            return
        print('Downloading Song Metadata')
        try:
            if 'https://www.youtube.com/watch?v=' in self.search_term:
                data = ytdl_metadata_link.extract_info(self.search_term, download=False)
            else:
                data = ytdl_metadata_search.extract_info('ytsearch:{%s}' % (self.search_term), download=False)['entries'][0]
        except:
            self.fucked = True
            return False
        self._title = data.get('title')
        self._url = data.get('url')
        return data
        

    @property
    def song_title(self):
        """
        Will return the title for the song.
        If the meta data is not downloaded yet, it will download the meta data
        """
        if not self._title:
            metadata = self.download_metadata()
            self._title = metadata.get('title')
            self._url = metadata.get('url')
        return self._title

    @property
    def url(self):
        """
        Will return the url for the song.
        If the meta data is not downloaded yet, it will download the meta data
        """
        if not self._url:
            metadata = self.download_metadata()
            self._title = metadata.get('title')
            self._url = metadata.get('url')
        return self._url

    def cleanup(self):
        """
        Free data that is being used by song
        """
        self.search_term = None
        self._title = None
        self._url = None
        if self._data:
            super().cleanup
        self._data = None

    def downloaded(self):
        return True if self._data else False
        

class Playlist():
    def __init__(self, playlist_link, start=1,pre_download=0):
        self._index = start
        self._link = playlist_link
        self._songindex = 1
        self._done_downloading = False
        self._songs = {}
        self._last_batch_data = None
        self._done_downloading = False
        self.active_song = None
        self._title = None
        #self._id = None

        self.songs_lock = Lock()
        self.index_lock = Lock()
        self.previous_batch_lock = Lock()
        self.song_index_lock = Lock()
    
    def download_metadata(self):
        """
        Will download the meta data for the playlist
        """
        if not self._title:
            print('Downloading Playlist Metadata')
            data = ytdl_metadata_playlist.extract_info(self._link, download=False)
            self._title = data.get('title')
            self._link = data.get('id')
            del data
            
    def change_song(self):
        """
        Will take a song form the pre-downloaded songs and move it to self.active_song
        If there are no pre-downloaded songs, then return False
        """
        if len(self) == 0:
            return False
        print('Playlist change song')
        self.song_index_lock.acquire()
        ind = self._songindex
        self._songindex += 1
        self.song_index_lock.release()

        self.songs_lock.acquire()
        self.active_song = self._songs.pop(ind)
        self.songs_lock.release()

                
        return self.active_song
            
    def download(self,n):
        """
        Will download n songs from the playlist

        will return how many songs it was able to download.
        Something like the playlist ending would cause this to be less than n.
        """
        print('playlist download songs')
        if self._done_downloading == True:
            return 0

        self.index_lock.acquire()
        ind = self._index
        self._index += n
        self.index_lock.release()

        self.previous_batch_lock.acquire()
        last_batch = self._last_batch_data
        self.previous_batch_lock.release()

        ytdl_temp = youtube_dl.YoutubeDL({
                            'format': 'bestaudio/best',
                            'noplaylist': False,
                            'playliststart':ind,
                            'playlistend':ind+n-1,
                            'quiet':True}
                             )
        data = ytdl_temp.extract_info(self._link,download=False)
        lst = []
        i = 0
        while i < n:
            if (last_batch != None) and last_batch['entries'][0] == data.get('entry'):
                self._done_downloading = True
                break
            lst.append([ind+i,Song('',data['entries'][i])])
            i += 1
        
        if not self._title:
            self._title = data.get('title')


        self.songs_lock.acquire()
        for item in lst:
            self._songs[item[0]] = item[1]
        self.songs_lock.release()
        
        self.previous_batch_lock.acquire()
        self._last_batch_data = data
        self.previous_batch_lock.release()
        return i

    def __len__(self):
        """
        returns how many songs the playlist has Pre-Downloaded
        """
        return len(self._songs)

    @property
    def current_song(self):
        """
        returns the current song in the playlist
        """
        return self.active_song
    
    @property
    def title(self):
        """
        returns the playlist title
        """
        if not self._title:
            self.download_metadata()
        return self._title

    @property
    def song_number(self):
        """
        returns the playlist song position
        """
        return self._index-len(self)

    def __str__(self):
        return str(self._songs)

class Song_Queue(deque):
    def __init__(self, min_buffer = 1,batch_size = 1):
        self.min_buffer = min_buffer
        self.batch_size = batch_size

        self._downloaded_songs = deque()
        self._not_downloaded_songs = deque()

        self.active_song = None
        self.main_lock = Lock()

    def clear(self):
        """
        Clears both deques and active song
        """
        self._downloaded_songs.clear()
        self._not_downloaded_songs.clear()
        self.active_song = None

    def change_song(self):
        print('song queue change song')
        self.main_lock.acquire()
        if isinstance(self.active_song, Playlist):
            has_songs = 1
            if len(self.active_song) == 0:
                return False
            
            if has_songs > 0:
                song = self.active_song.change_song()
                
                return song

        if len(self._downloaded_songs) == 0:
            self.active_song = None
            return False
        
        elem = self._downloaded_songs.popleft()
        self.active_song = elem
        if isinstance(elem, Playlist):
            elem = elem.change_song()
        self.main_lock.release()
        return elem
    
    def remove_element(self, n):
        """
        Removes the Nth element from the song_queue
        """
        print('song queue remove elem')
        self.main_lock.acquire()
        if n == 0:
            self.active_song = None
        if n > (len(self._downloaded_songs) + len(self._not_downloaded_songs)):
            return False
        counter = 0
        while(counter < len(self._downloaded_songs)):
            n -= 1
            if n == 0:
                del self._downloaded_songs[counter]
            counter += 1
        counter = 0
        while(counter < (len(self._downloaded_songs)+len(self._not_downloaded_songs))):
            n -= 1
            if n == 0:
                del self._not_downloaded_songs[counter]
            counter += 1
        self.main_lock.release()
        
    def download(self,n):
        """
        Downloads the next n songs from self._not_downloaded_songs and puts them into self._downloaded_songs
        """
        print('song queue download')
        i = 0
        if isinstance(self.active_song, Playlist):
            i += self.active_song.download(n)
        while(i<n):
            if len(self._not_downloaded_songs) == 0:
                return
            elem = self._not_downloaded_songs[0]
            if isinstance(elem, Song):
                #Elem is a song
                if elem.download():             
                    i += 1
                else:
                    print('fuck')
                    self._not_downloaded_songs.popleft()
                    elem.cleanup()
                    continue
            else:
                #Elem is a playlist
                num_downloaded = elem.download(n)
                i += num_downloaded
            self._not_downloaded_songs.popleft()
            self._downloaded_songs.append(elem)

        return i

            

    def add_bottom(self, elem):
        """
        Adds a song to the bottom of the song_queue
        checks if a new batch of songs needs to be downloaded in order to fill the buffer
        downloads the meta data of the new song
        """
        print('song queue add bottom')
        if isinstance(elem, Song) and elem.downloaded:
            self._downloaded_songs.append(elem)
        else:
            self._not_downloaded_songs.append(elem)
        if len(self)<self.min_buffer:
            self.download(self.batch_size)
        
    def add_top(self, elem):
        print('song queue add top')
        if not self.active_song:
            self.add_bottom(elem)
            return
        if isinstance(elem, Playlist):
            elem.download(1)

        if isinstance(self.active_song, Song):
            self._downloaded_songs.appendleft(elem)
        else:
            self._downloaded_songs.appendleft(self.active_song)
            self.active_song = self.active_song.current_song
            self._downloaded_songs.appendleft(elem)
        
    def __len__(self):
        elem = self.active_song
        l = 0
        if isinstance(elem, Playlist):
            l = len(elem)-1
        return len(self._downloaded_songs) + l


    def __str__(self):
        """
        returns the song_queue as a string.
        This is only really useful for $queue
        """
        print('Song Queue String')
        elem = self.active_song
        if isinstance(elem, Playlist):
            string = '''on Song %i of: %s\n\n''' % (elem.song_number-1, elem.title)
        else:
            string = ''': %s\n\n''' % elem.song_title
        
        i = 0
        #string += '''Pre-Loaded Songs:\n'''
        string += '''Songs:\n'''
        while(i<len(self._downloaded_songs)):
            elem = self._downloaded_songs[i]
            if isinstance(elem, Song):
                string += '%i- %s\n' % (i+1, elem.song_title)
            else:
                string += '%i- On Song %i of: %s\n' % (i+1,elem.song_number,elem.title)
            i += 1

        #string += '''\nUn-Loaded Songs:\n'''
        while(i<len(self._downloaded_songs)+len(self._not_downloaded_songs)):
            elem = self._not_downloaded_songs[i-len(self._downloaded_songs)]
            if isinstance(elem, Song):
                string += '%i- %s\n' % (i+1, elem.song_title)
            else:
                string += '%i- On Video %i in %s\n' % (i+1,elem.song_number,elem.title)
            i += 1
        return string
    
class Guild_Info():
    def __init__(self):
        self._song_lists = Song_Queue()

    @property
    def song_queue(self):
        """
        Returns the song_queue object for the guild.
        You can call this like a property
        """
        return self._song_lists

    @property
    def current_song(self):
        """
        Returns the song that is currently playing in the server.
        You can call this like a property
        """
        elem = self._song_lists.active_song
        if isinstance(elem, Playlist):
            elem = elem.current_song
        return elem

    def clear_queue(self):
        """
        This will clear the song_queue object.
        You can call this like a property
        """
        self._song_lists.clear()
        self._currently_playing = None
