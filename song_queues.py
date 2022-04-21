import collections
import math
import functools

class Song_Queue():
    """
    Every perons places a song into a queue. These songs are played sequentally.
    """
    def __init__(self, preload_count = 1):
        self.loaded = collections.deque()
        self.unloaded = collections.deque()
        self.preload_count = preload_count
        self.current_song = None

    @property
    def loaded_len(self):
        return len(self.loaded) + (0 if self.current_song == None else 1)

    @property
    def pre_loaded_len(self):
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
        if (self.pre_loaded_len < self.preload_count):
            self.download(self.preload_count - self.pre_loaded_len)

    def __getitem__(self, index):
        if index < 0:
            raise NotImplementedError()

        if (index < len(self.loaded)):
            return self.loaded[index]
        else:
            return self.unloaded[index-len(self.loaded)]

    def __len__(self):
        return len(self.loaded) + len(self.unloaded)

    def __bool__(self):
        return True if (self.current_song) else False

    def __str__(self):
        string = ""
        for i in range(len(self)):
            string += str(i+1)+ ". " +self[i].title + "\n"
        return string

class Authored_Queue(Song_Queue):
    def __init__(self, author_id):
        super().__init__(preload_count=0)
        self.author_id = author_id
        

class Song_Rotator():
    """
    Every person places a song into a queue. 
    Each person with songs in the queue, plays one song, 
    then the next person plays one of thier songs.
    """
    def __init__(self, preload_count):
        # {Author_id : Authored_Queue}
        self.author_queue_dict = {}
        self.author_queue_deque = collections.deque()

        # TODO: Dynamic preload count.
        # Song Rotators are currenly only built to have a prelaod value of 1.
        self.preload_count = 1
    
    @property
    def current_song(self):
        if (not self.author_queue_deque):
            return None
        return self.author_queue_deque[0].current_song

    @property
    def loaded_len(self):
        #TODO: Change this to reduce
        sum = 0
        for queue in self.author_queue_deque:
            sum += queue.loaded_len
        return sum

    @property
    def pre_loaded_len(self):
        #TODO: Change this to reduce
        sum = 0
        for queue in self.author_queue_deque:
            sum += queue.pre_loaded_len
        return sum

    def download(self, n):
        # TODO: Update this function to download the next n songs,
        # instead of a few songs in the fist author queues

        n = 1
        for i in range(len(self.author_queue_deque)):
            self.author_queue_deque[i].download(n//len(self.author_queue_deque))

        for i in range(n%len(self.author_queue_deque)):
            self.author_queue_deque[i].download(1)
        
    def change_song(self):
        if (not self.author_queue_deque):
            #There are no more songs
            return
        
        self.author_queue_deque[0].change_song()

        if (not self.author_queue_deque[0].current_song):
            #The author ran out of songs to play, remove them
            author = self.author_queue_deque.pop()
            del self.author_queue_dict[author.author_id]
            self.change_song()
            return
        
        self.author_queue_deque.rotate(-1)
        self.check_preload()
        
        return self.author_queue_deque[0].current_song
        
    def append(self, song):
        if (song.requester not in self.author_queue_dict):
            author_queue = Authored_Queue(song.requester)
            self.author_queue_dict[song.requester] = author_queue
            self.author_queue_deque.append(author_queue)
        
        self.author_queue_dict[song.requester].append(song)
        self.check_preload()

    def check_preload(self):
        if (self.pre_loaded_len < self.preload_count):
            self.download(self.preload_count - self.pre_loaded_len)

    def __len__(self):
        #TODO: Change this to reduce
        sum = 0
        for queue in self.author_queue_deque:
            sum += len(queue)
        return sum

    def __bool__(self):
        return True if (self.author_queue_dict) else False

    def __str__(self):
        string = ""
        for author_queue in self.author_queue_deque:
            string += "<@" + str(author_queue.author_id)+ "> - " +author_queue.current_song.title + "\n"
        return string
