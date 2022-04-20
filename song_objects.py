import discord
import collections
import ytdl_config

class Song_Queue():
    def __init__(self, preload_count = 1):
        self.loaded = collections.deque()
        self.unloaded = collections.deque()
        self.preload_count = preload_count
        self.current_song = None

    @property
    def loaded_len(self):
        #THIS DOES NOT WORK WITH PLAYLISTS
        return len(self.loaded)

    def download(self, n):
        """
        Will attempt to downlaod n songs from the unloaded deque
        After downloading a song it will be moved to the loaded deque
        """
        while(n>0):
            
            if (not self.unloaded):
                #There are no songs to download
                return

            element_to_download = self.unloaded[0]
            num_downloaded, err = element_to_download.download(n)

            if (err):
                print(err)
                return

            n -= num_downloaded
            self.loaded.append(element_to_download)
            if (element_to_download.data_downloaded):
                #If the element has no more songs to download
                self.unloaded.remove(element_to_download)
        return

    def change_song(self):
        #THIS DOES NOT WORK WITH PLAYLISTS
        if self.loaded:
            self.current_song = self.loaded.pop()
            self.check_preload()
        else:
            self.current_song = None
        
        return self.current_song
        
    def append(self, song):
        self.unloaded.append(song)
        self.check_preload()

    def check_preload(self):
        if (self.loaded_len < self.preload_count):
            self.download(self.preload_count - self.loaded_len)


class Song(discord.PCMVolumeTransformer):
    def __init__(self, search_term, download_settings):
        self.data_downloaded = False
        self.metadata_downloaded = False
        self.data = None

        self.search_term = search_term
        self.download_settings = download_settings

        #TODO Locking Here
        
    def download(self, n=1):
        """
        Will download the full song. This takes a long time and a lot of space.
        It is preferable to just download the metadata of the song if that is all that is needed at the moment.
        """
        if self.data_downloaded:
            #Already downloaded
            return 0

        try:
            self.data = self.download_settings.download_video(self.search_term)
        except Exception as e:
            return 0, str(e)

        self.data_downloaded = True
        self.metadata_downloaded = True

        super().__init__(discord.FFmpegPCMAudio(self.data.get('url'), **ytdl_config.ffmpeg_options))
        
        return 1, ""

    def download_metadata(self, n=1):
        """
        Downloads information about the song, but does not download the actual song.
        Will download information like, title, url.
        Signifigantly faster than downloading the entire song.
        """
        if self.metadata_downloaded:
            # Already downloaded
            return 0

        try:
            self.data = self.download_settings.metadata.extract_info(self.search_term, download=False)
        except Exception as e:
            return str(e)
        
        self.metadata_downloaded = True
        
        return 1
    
    @property
    def is_downloaded(self):
        return self.data_downloaded

    @property
    def title(self):
        return self.data.get("title") if (self.metadata_downloaded) else None

    @property
    def url(self):
        return self.data.get("url") if (self.metadata_downloaded) else None

    def loaded_len(self):
        return 1 if self.is_downloaded else 0

class Playlist(Song_Queue):
    def __init__(self):
        self.loaded = collections.deque()
        self.unloaded = collections.deque()
        self.index = 0

    def download(self, n):
        return 1

    def download_metadata(self, n):
        return 1




