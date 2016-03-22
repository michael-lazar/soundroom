import os
import time

from include import vlc

"""
Need to figure out which features libvlc is capable of
  1. Streaming
  2. Recording
  3. Read audio file into samples array
  4. Create audio file using samples
  5. Controlling audio device
  6. Converting to different formats

What I know for sure it can do
  1. Read encoded audio (MP3, FLAC, etc)
  2. Play audio
  3. Read directly from url
"""


class Player(object):

    # NothingSpecial, Opening, Buffering, Playing, Paused, Stopped, Ended, Error
    State = vlc.State

    def __init__(self, source):
        # Load from...
        #   "file://home/user/Music/audio.wav"
        #   "/home/user/Music/audio.wav"
        #   "relative/path/audio.wav"
        #   "relative/to/project/audio.wav"
        #   "http://website.com/audio.wav"
        #   file-like object
        #   bytes (python 2/3 fun!)
        #   samples / samplerate (write to temp wav file?)

        self._instance = vlc.Instance()
        self._media = self._instance.media_new(source)
        self._player = self._instance.media_player_new()
        self._player.set_media(self._media)

    def play(self):
        out = self._player.play()
        if out == -1:
            raise ValueError('Could not play source')

    def pause(self):
        self._player.set_pause(1)

    def stop(self):
        self._player.stop()

    def seek(self, position):
        i_time = int(position * 1000)
        self._player.set_time(i_time)

    def rewind(self):
        self.seek(0)

    @property
    def volume(self):
        return self._player.audio_get_volume()

    @volume.setter
    def volume(self, val):
        out = self._player.audio_set_volume(val)
        if out == -1:
            raise ValueError('Volume out of range')

    @property
    def position(self):
        out = self._player.get_time()
        if out != -1:
            out /= 1000.0
        return out

    @property
    def is_playing(self):
        return self._player.is_playing()


if __name__ == '__main__':

    root = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(root, 'resources', 'jeopardy.mp3')

    player = Player(filename)
    player.play()
    time.sleep(2.0)
    player.pause()
    time.sleep(2.0)
    player.play()
    time.sleep(2.0)
    player.volume = 50
    time.sleep(2.0)
    player.rewind()
    time.sleep(2.0)