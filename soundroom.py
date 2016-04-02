import os
import time
from ctypes import *

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


# class EventManager(_Ctype):
#     '''Create an event manager with callback handler.
#
#     This class interposes the registration and handling of
#     event notifications in order to (a) remove the need for
#     decorating each callback functions with the decorator
#     '@callbackmethod', (b) allow any number of positional
#     and/or keyword arguments to the callback (in addition
#     to the Event instance) and (c) to preserve the Python
#     objects such that the callback and argument objects
#     remain alive (i.e. are not garbage collected) until
#     B{after} the notification has been unregistered.
#
#     @note: Only a single notification can be registered
#     for each event type in an EventManager instance.
#
#     '''
#
#     _callback_handler = None
#     _callbacks = {}
#
#     def __new__(cls, ptr=_internal_guard):
#         if ptr == _internal_guard:
#             raise VLCException("(INTERNAL) ctypes class.\nYou should get a reference to EventManager through the MediaPlayer.event_manager() method.")
#         return _Constructor(cls, ptr)
#
#     def event_attach(self, eventtype, callback, *args, **kwds):
#         """Register an event notification.
#
#         @param eventtype: the desired event type to be notified about.
#         @param callback: the function to call when the event occurs.
#         @param args: optional positional arguments for the callback.
#         @param kwds: optional keyword arguments for the callback.
#         @return: 0 on success, ENOMEM on error.
#
#         @note: The callback function must have at least one argument,
#         an Event instance.  Any other, optional positional and keyword
#         arguments are in B{addition} to the first one.
#         """
#         if not isinstance(eventtype, EventType):
#             raise VLCException("%s required: %r" % ('EventType', eventtype))
#         if not hasattr(callback, '__call__'):  # callable()
#             raise VLCException("%s required: %r" % ('callable', callback))
#          # check that the callback expects arguments
#         if not any(getargspec(callback)[:2]):  # list(...)
#             raise VLCException("%s required: %r" % ('argument', callback))
#
#         if self._callback_handler is None:
#             _called_from_ctypes = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
#             @_called_from_ctypes
#             def _callback_handler(event, k):
#                 """(INTERNAL) handle callback call from ctypes.
#
#                 @note: We cannot simply make this an EventManager
#                 method since ctypes does not prepend self as the
#                 first parameter, hence this closure.
#                 """
#                 try: # retrieve Python callback and arguments
#                     call, args, kwds = self._callbacks[k]
#                      # deref event.contents to simplify callback code
#                     call(event.contents, *args, **kwds)
#                 except KeyError:  # detached?
#                     pass
#             self._callback_handler = _callback_handler
#             self._callbacks = {}
#
#         k = eventtype.value
#         r = libvlc_event_attach(self, k, self._callback_handler, k)
#         if not r:
#             self._callbacks[k] = (callback, args, kwds)
#         return r
#
#     def event_detach(self, eventtype):
#         """Unregister an event notification.
#
#         @param eventtype: the event type notification to be removed.
#         """
#         if not isinstance(eventtype, EventType):
#             raise VLCException("%s required: %r" % ('EventType', eventtype))
#
#         k = eventtype.value
#         if k in self._callbacks:
#             del self._callbacks[k] # remove, regardless of libvlc return value
#             libvlc_event_detach(self, k, self._callback_handler, k)


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

        self._pointer = c_void_p()

        @vlc.CallbackDecorators.LogCb
        def cb(*args, **kwargs):
            return self._pointer

        self._instance.log_set(cb, self._pointer)

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

    # player = Player(filename)
    player = Player('http://us1.internet-radio.com:11094/listen.pls')
    # player = Player('https://www.youtube.com/watch?v=UGPxKcFYLMk')
    player.play()
    # player.rate(4.0)
    time.sleep(1)
    print 'hi'
    # time.sleep(10)
    # player.pause()
    # time.sleep(2.0)
    # player.play()
    # time.sleep(2.0)
    # player.volume = 50
    # time.sleep(2.0)
    # player.rewind()
    # time.sleep(2.0)
#
#
# class LogLevel(_Enum):
#     '''Logging messages level.
# \note future libvlc versions may define new levels.
#     '''
#     _enum_names_ = {
#         0: 'DEBUG',
#         2: 'NOTICE',
#         3: 'WARNING',
#         4: 'ERROR',
#     }
# LogLevel.DEBUG   = LogLevel(0)
# LogLevel.ERROR   = LogLevel(4)
# LogLevel.NOTICE  = LogLevel(2)
# LogLevel.WARNING = LogLevel(3)
#
# class CallbackDecorators(object):
#     LogCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, Log_ptr, ctypes.c_char_p, ctypes.c_void_p)
#     LogCb.__doc__ = '''Callback prototype for LibVLC log message handler.
# \param data data pointer as given to L{libvlc_log_set}()
# \param level message level (@ref libvlc_log_level)
# \param ctx message context (meta-information about the message)
# \param fmt printf() format string (as defined by ISO C11)
# \param args variable argument list for the format
# \note Log message handlers <b>must</b> be thread-safe.
# \warning The message context pointer, the format string parameters and the
#          variable arguments are only valid until the callback returns.
#     '''
#
# class LogCb(ctypes.c_void_p):
#     pass
#
# # Wrapper for the opaque struct libvlc_log_t
# class Log(ctypes.Structure):
#     pass
# Log_ptr = ctypes.POINTER(Log)
#
# class LogMessage(_Cstruct):
#     _fields_ = [
#         ('size',     ctypes.c_uint  ),
#         ('severity', ctypes.c_int   ),
#         ('type',     ctypes.c_char_p),
#         ('name',     ctypes.c_char_p),
#         ('header',   ctypes.c_char_p),
#         ('message',  ctypes.c_char_p),
#     ]
#
#     def __init__(self):
#         super(LogMessage, self).__init__()
#         self.size = ctypes.sizeof(self)
#
#     def __str__(self):
#         return '%s(%d:%s): %s' % (self.__class__.__name__, self.severity, self.type, self.message)
#
# class EventManager(_Ctype):
#     '''Create an event manager with callback handler.
#
#     This class interposes the registration and handling of
#     event notifications in order to (a) remove the need for
#     decorating each callback functions with the decorator
#     '@callbackmethod', (b) allow any number of positional
#     and/or keyword arguments to the callback (in addition
#     to the Event instance) and (c) to preserve the Python
#     objects such that the callback and argument objects
#     remain alive (i.e. are not garbage collected) until
#     B{after} the notification has been unregistered.
#
#     @note: Only a single notification can be registered
#     for each event type in an EventManager instance.
#
#     '''
#
#     _callback_handler = None
#     _callbacks = {}
#
#     def __new__(cls, ptr=_internal_guard):
#         if ptr == _internal_guard:
#             raise VLCException("(INTERNAL) ctypes class.\nYou should get a reference to EventManager through the MediaPlayer.event_manager() method.")
#         return _Constructor(cls, ptr)
#
#     def event_attach(self, eventtype, callback, *args, **kwds):
#         """Register an event notification.
#
#         @param eventtype: the desired event type to be notified about.
#         @param callback: the function to call when the event occurs.
#         @param args: optional positional arguments for the callback.
#         @param kwds: optional keyword arguments for the callback.
#         @return: 0 on success, ENOMEM on error.
#
#         @note: The callback function must have at least one argument,
#         an Event instance.  Any other, optional positional and keyword
#         arguments are in B{addition} to the first one.
#         """
#         if not isinstance(eventtype, EventType):
#             raise VLCException("%s required: %r" % ('EventType', eventtype))
#         if not hasattr(callback, '__call__'):  # callable()
#             raise VLCException("%s required: %r" % ('callable', callback))
#          # check that the callback expects arguments
#         if not any(getargspec(callback)[:2]):  # list(...)
#             raise VLCException("%s required: %r" % ('argument', callback))
#
#         if self._callback_handler is None:
#             _called_from_ctypes = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
#             @_called_from_ctypes
#             def _callback_handler(event, k):
#                 """(INTERNAL) handle callback call from ctypes.
#
#                 @note: We cannot simply make this an EventManager
#                 method since ctypes does not prepend self as the
#                 first parameter, hence this closure.
#                 """
#                 try: # retrieve Python callback and arguments
#                     call, args, kwds = self._callbacks[k]
#                      # deref event.contents to simplify callback code
#                     call(event.contents, *args, **kwds)
#                 except KeyError:  # detached?
#                     pass
#             self._callback_handler = _callback_handler
#             self._callbacks = {}
#
#         k = eventtype.value
#         r = libvlc_event_attach(self, k, self._callback_handler, k)
#         if not r:
#             self._callbacks[k] = (callback, args, kwds)
#         return r
#
#     def event_detach(self, eventtype):
#         """Unregister an event notification.
#
#         @param eventtype: the event type notification to be removed.
#         """
#         if not isinstance(eventtype, EventType):
#             raise VLCException("%s required: %r" % ('EventType', eventtype))
#
#         k = eventtype.value
#         if k in self._callbacks:
#             del self._callbacks[k] # remove, regardless of libvlc return value
#             libvlc_event_detach(self, k, self._callback_handler, k)
#
#
# class Instance(_Ctype):
#     def log_unset(self):
#         '''Unsets the logging callback for a LibVLC instance. This is rarely needed:
#         the callback is implicitly unset when the instance is destroyed.
#         This function will wait for any pending callbacks invocation to complete
#         (causing a deadlock if called from within the callback).
#         @version: LibVLC 2.1.0 or later.
#         '''
#         return libvlc_log_unset(self)
#
#
#     def log_set(self, data, p_instance):
#         '''Sets the logging callback for a LibVLC instance.
#         This function is thread-safe: it will wait for any pending callbacks
#         invocation to complete.
#         @param data: opaque data pointer for the callback function @note Some log messages (especially debug) are emitted by LibVLC while is being initialized. These messages cannot be captured with this interface. @warning A deadlock may occur if this function is called from the callback.
#         @param p_instance: libvlc instance.
#         @version: LibVLC 2.1.0 or later.
#         '''
#         return libvlc_log_set(self, data, p_instance)
#
#
#     def log_set_file(self, stream):
#         '''Sets up logging to a file.
#         @param stream: FILE pointer opened for writing (the FILE pointer must remain valid until L{log_unset}()).
#         @version: LibVLC 2.1.0 or later.
#         '''
#
# def libvlc_log_get_context(ctx):
#     '''Gets debugging information about a log message: the name of the VLC module
#     emitting the message and the message location within the source code.
#     The returned module name and file name will be None if unknown.
#     The returned line number will similarly be zero if unknown.
#     @param ctx: message context (as passed to the @ref libvlc_log_cb callback).
#     @return: module module name storage (or None), file source code file name storage (or None), line source code file line number storage (or None).
#     @version: LibVLC 2.1.0 or later.
#     '''
#     f = _Cfunctions.get('libvlc_log_get_context', None) or \
#         _Cfunction('libvlc_log_get_context', ((1,), (2,), (2,), (2,),), None,
#                     None, Log_ptr, ListPOINTER(ctypes.c_char_p), ListPOINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_uint))
#     return f(ctx)
#
# def libvlc_log_get_object(ctx, id):
#     '''Gets VLC object information about a log message: the type name of the VLC
#     object emitting the message, the object header if any and a temporaly-unique
#     object identifier. This information is mainly meant for B{manual}
#     troubleshooting.
#     The returned type name may be "generic" if unknown, but it cannot be None.
#     The returned header will be None if unset; in current versions, the header
#     is used to distinguish for VLM inputs.
#     The returned object ID will be zero if the message is not associated with
#     any VLC object.
#     @param ctx: message context (as passed to the @ref libvlc_log_cb callback).
#     @return: name object name storage (or None), header object header (or None), line source code file line number storage (or None).
#     @version: LibVLC 2.1.0 or later.
#     '''
#     f = _Cfunctions.get('libvlc_log_get_object', None) or \
#         _Cfunction('libvlc_log_get_object', ((1,), (2,), (2,), (1,),), None,
#                     None, Log_ptr, ListPOINTER(ctypes.c_char_p), ListPOINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_uint))
#     return f(ctx, id)
#
# def libvlc_log_unset(p_instance):
#     '''Unsets the logging callback for a LibVLC instance. This is rarely needed:
#     the callback is implicitly unset when the instance is destroyed.
#     This function will wait for any pending callbacks invocation to complete
#     (causing a deadlock if called from within the callback).
#     @param p_instance: libvlc instance.
#     @version: LibVLC 2.1.0 or later.
#     '''
#     f = _Cfunctions.get('libvlc_log_unset', None) or \
#         _Cfunction('libvlc_log_unset', ((1,),), None,
#                     None, Instance)
#     return f(p_instance)
#
# def libvlc_log_set(cb, data, p_instance):
#     '''Sets the logging callback for a LibVLC instance.
#     This function is thread-safe: it will wait for any pending callbacks
#     invocation to complete.
#     @param cb: callback function pointer.
#     @param data: opaque data pointer for the callback function @note Some log messages (especially debug) are emitted by LibVLC while is being initialized. These messages cannot be captured with this interface. @warning A deadlock may occur if this function is called from the callback.
#     @param p_instance: libvlc instance.
#     @version: LibVLC 2.1.0 or later.
#     '''
#     f = _Cfunctions.get('libvlc_log_set', None) or \
#         _Cfunction('libvlc_log_set', ((1,), (1,), (1,),), None,
#                     None, Instance, LogCb, ctypes.c_void_p)
#     return f(cb, data, p_instance)
#
# def libvlc_log_set_file(p_instance, stream):
#     '''Sets up logging to a file.
#     @param p_instance: libvlc instance.
#     @param stream: FILE pointer opened for writing (the FILE pointer must remain valid until L{libvlc_log_unset}()).
#     @version: LibVLC 2.1.0 or later.
#     '''
#     f = _Cfunctions.get('libvlc_log_set_file', None) or \
#         _Cfunction('libvlc_log_set_file', ((1,), (1,),), None,
#                     None, Instance, FILE_ptr)
#     return f(p_instance, stream)
#
# def debug_callback(event, *args, **kwds):
#     '''Example callback, useful for debugging.
#     '''
#     l = ['event %s' % (event.type,)]
#     if args:
#         l.extend(map(str, args))
#     if kwds:
#         l.extend(sorted('%s=%s' % t for t in kwds.items()))
#     print('Debug callback (%s)' % ', '.join(l))
#
# The function prototype can be called in different ways to create a
# callable object:
#
# prototype(integer address) -> foreign function
# prototype(callable) -> create and return a C callable function from callable
# prototype(integer index, method name[, paramflags]) -> foreign function calling a COM method
# prototype((ordinal number, dll object)[, paramflags]) -> foreign function exported by ordinal
# prototype((function name, dll object)[, paramflags]) -> foreign function exported by name