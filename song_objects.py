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
        """Downloads the first n songs in the queue.

        Once a song and playlist is downloaded from the front of theunloaded deque, it is 
        then moved to the end of the loaded deque.
        
        If a playlist is partially downloaded, and partially not downloaded, then it
        will be in both self.loaded and self.unloaded.

        Parameters
        ----------
        n : int
            The desired number of songs to download. It will download up to n songs.
            If there are less than n songs, it will download all the songs, then return.

        Return
        ------
        None
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

    def __getitem__(self, index):
        if index < 0:
            raise NotImplementedError()

        if (index < len(self.loaded)):
            return self.loaded[index]
        else:
            return self.unloaded[index-len(self.loaded)]

    def __len__(self):
        return len(self.loaded) + len(self.unloaded)


class Song(discord.PCMVolumeTransformer):
    def __init__(self, search_term, download_settings):
        self.data_downloaded = False
        self.metadata_downloaded = False
        self.data = None

        self.search_term = search_term
        self.download_settings = download_settings

        #TODO: Only download the meta data when it is called, instead of when the object is created
        self.download_metadata() 

        #TODO Locking Here 🔒
        
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