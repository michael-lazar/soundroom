import os
import time

from include import vlc

"""
Notable audio packages
----------------------

Pydub (ffmpeg or libav)
  - Load file into samples
  - Write samples to file
  - Play samples (no controls)

python-sounddevice (PortAudio)
  - Play samples
  - Record to samples
  - Streaming but no controls

audiolab (libsndfile)
  - Load file into samples (limited set of files)
  - Play samples (no controls)

pysndfile (libsndfile)
  - Low level reading and writing files (limited set)

pyglet (OpenAL, AVbin)
  - Play all types of files
  - Media controls (pause, volume, etc.)
  - Large install

PyAudio (PortAudio)
  - Low level playing and recording data

Audiere (abandoned)
PyMedia (abandoned)

What libvlc provides
--------------------

- Simple installation
- Read encoded audio (MP3, etc.)
- Play directly from url / stream
- Full, stable media controls

What libvlc can't do
--------------------

- Record audio
- Load audio as samples / export samples
- Convert file formats
"""

"""
MediaType: unknown, file, directory, disc, stream, playlist
State: NothingSpecial, Opening, Buffering, Playing, Paused, Stopped, Ended, Error
Meta
AudioOutputDeviceTypes
AudioOutputChannel

AudioPlayCb

channels
"""


class Player(object):

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
        if self._player.can_pause():
            self._player.set_pause(1)

    def stop(self):
        self._player.stop()

    def seek(self, position):
        if self._player.is_seekable():
            i_time = int(position * 1000)
            self._player.set_time(i_time)

    def rate(self, rate):
        self._player.set_rate(rate)

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

    player = Player('http://us1.internet-radio.com:11094/listen.pls')
    player.play()
    time.sleep(20.0)
    # player.rate(2)
    # time.sleep(10)
    # player.pause()
    # time.sleep(2.0)
    # player.play()
    # time.sleep(2.0)
    # player.volume = 50
    # time.sleep(2.0)
    # player.rewind()
    # time.sleep(2.0)