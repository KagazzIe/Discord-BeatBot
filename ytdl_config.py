import youtube_dl

class ytdl_options():
    def __init__(self, video, metadata):
        self.video = youtube_dl.YoutubeDL(video)
        self.metadata = youtube_dl.YoutubeDL(metadata)

ytdl_search = ytdl_options(
    {'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto',
    'quiet':False},

    {'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto',
    'skip_download':True,
    'simulate':True,
    'quiet':False}
)

ytdl_url = ytdl_options(
    {'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet':False},

    {'format': 'bestaudio/best',
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