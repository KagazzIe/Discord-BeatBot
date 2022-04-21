import discord
import collections
import ytdl_config
import song_queues

class Song(discord.PCMVolumeTransformer):
    def __init__(self, search_term, download_settings, author_id):
        self.data_downloaded = False
        self.metadata_downloaded = False
        self.data = None
        self.requester = author_id

        self.search_term = search_term
        self.download_settings = download_settings

        #TODO: Only download the meta data when it is called, instead of when the object is created
        self.download_metadata()

        
    def download(self, n=1):
        """Downloads the information about the song and downloads the actual song. 
        Much slower than download_metadata.

        If the self.downloaded Bool is set to true, then the function will be aborted,
        and time will not be spent re-downloading information.

        After sucessfully completing this function, self.metadata_downloaded and 
        self.downloaded will be set to True.

        Parameters
        ----------
        n : int, optional
            The desired number of songs to download. This is not very useful for Song()
            objects, but becomes useful when working with Playlist()

        Return
        ------
        int
           This will return the number of songs that successfully downloaded.
           For the Song() object, this will always be 1 or 0.
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
        """Downloads information about the song. Much Faster than download.

        If the self.metadata_downloaded Bool is set to true, then the function will be aborted,
        and time will not be spent re-downloading information.

        After sucessfully completing this function, self.metadata_downloaded 
        will be set to True.

        Parameters
        ----------
        n : int, optional
            The desired number of songs to download. This is not very useful for Song()
            objects, but becomes useful when working with Playlist()

        Return
        ------
        int
           This will return the number of songs that successfully downloaded.
           For the Song() object, this will always be 1 or 0.
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

    @property
    def loaded_len(self):
        return 1 if self.is_downloaded else 0

class Playlist(song_queues.Song_Queue):
    def __init__(self):
        self.loaded = collections.deque()
        self.unloaded = collections.deque()
        self.index = 0

    def download(self, n):
        return 1

    def download_metadata(self, n):
        return 1