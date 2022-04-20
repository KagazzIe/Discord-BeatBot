import discord
import collections
import ytdl_config

class Song_Queue():
    def __init__(self, preload_count = 0):
        self.loaded = collections.deque()
        self.unloaded = collections.deque()
        self.preload_count = preload_count

    def __len__(self):
        pass

    def loaded_len(self):
        pass

    def download(self, n):
        pass

    def remove(self, n):
        pass

    def change_song(self):
        pass
        
    def append(self):
        pass

    def add_top(self):
        pass

    def clear(self):
        pass

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
            return str(e)

        self.data_downloaded = True
        self.metadata_downloaded = True

        super().__init__(discord.FFmpegPCMAudio(self.data.get('url'), **ytdl_config.ffmpeg_options))
        
        return

    def download_metadata(self, n):
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




