from aptdaemon import loop
import sys, time, thread
import gst
import pygst
import urllib2
import ast
import random
from PyQt4 import QtGui
import sys, os, time, thread
import glib, gobject
import pygst
import gst

# http://gstreamer.freedesktop.org/documentation/
# http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-playbin.html
# https://developers.soundcloud.com
# http://stackoverflow.com/questions/2745076/what-is-the-difference-between-git-commit-and-git-push
# http://stackoverflow.com/questions/20460296/playing-remote-audio-files-in-python
#http://pygstdocs.berlios.de/pygst-reference/class-gstelement.html


class PoolSidePlayer(QtGui.QWidget):

    def __init__(self):
        super(PoolSidePlayer, self).__init__()

        self.tracks = self.get_all_tracks()

        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        self.initUI()

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.playmode = False
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playmode = False

    @staticmethod
    def get_all_tracks():
        response = urllib2.urlopen("http://poolsideapi2.herokuapp.com/tracks")
        tracks = ast.literal_eval(response.read())
        return tracks

    def shuffle_tracks(self):
        self.tracks = self.get_all_tracks()
        random.shuffle(self.tracks)

    def play_tracks(self):
        self.shuffle_tracks()
        for curr_track in self.tracks:
            self.playmode = True
            self.player.set_property("uri", 'http://api.soundcloud.com/tracks/%s/stream?client_id=e72237107739281ffceb867534efd87c' \
                           % curr_track['scId'])
            self.player.set_state(gst.STATE_PLAYING)
            while self.playmode:
                time.sleep(1)

        time.sleep(1)
        loop.quit()


    def play(self):
        if self.player.get_state()[1] == gst.STATE_PLAYING:
            self.player.set_state(gst.STATE_PAUSED)
        elif self.player.get_state()[1] == gst.STATE_PAUSED:
            self.player.set_state(gst.STATE_PLAYING)
        else:
            thread.start_new_thread(self.play_tracks, ())
            gobject.threads_init()
            loop = glib.MainLoop()
            loop.run()

    def skip(self):
        self.player.set_state(gst.STATE_NULL)
        self.play()

    def initUI(self):

        play_btn = QtGui.QPushButton('Play/Pause', self)
        play_btn.resize(play_btn.sizeHint())
        play_btn.clicked.connect(self.play)
        play_btn.move(60, 250)

        skip_btn = QtGui.QPushButton('Skip', self)
        skip_btn.resize(skip_btn.sizeHint())
        skip_btn.clicked.connect(self.skip)
        skip_btn.move(160, 250)

        self.setFixedSize(300, 300)
        self.setWindowTitle('Poolside FM')
        self.show()

def main():

    app = QtGui.QApplication(sys.argv)
    ex = PoolSidePlayer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()