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
import threading
from multiprocessing import Process

# http://gstreamer.freedesktop.org/documentation/
# http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-playbin.html
# https://developers.soundcloud.com
# http://stackoverflow.com/questions/2745076/what-is-the-difference-between-git-commit-and-git-push
# http://stackoverflow.com/questions/20460296/playing-remote-audio-files-in-python
#http://pygstdocs.berlios.de/pygst-reference/class-gstelement.html
class PoolSideStream():
    def __init__(self):
        self.tracks = self.get_all_tracks()
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

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
        random.shuffle(tracks)
        return tracks

    def play_tracks(self):
        random.shuffle(self.tracks)
        for curr_track in self.tracks:
            self.playmode = True
            self.player.set_property("uri", 'http://api.soundcloud.com/tracks/%s/stream?client_id=e72237107739281ffceb867534efd87c' \
                           % curr_track['scId'])
            self.player.set_state(gst.STATE_PLAYING)
            while self.player.get_state()[1] != gst.STATE_NULL:
                time.sleep(1)
                print "Playing track: %s" % curr_track['scId']

        time.sleep(1)

    def play(self):
        self.player.set_state(gst.STATE_PLAYING)

    def pause(self):
        self.player.set_state(gst.STATE_PAUSED)

    def stop(self):
        self.player.set_state(gst.STATE_NULL)

    def get_state(self):
        return self.player.get_state()[1]


class PoolSidePlayer(QtGui.QWidget):

    def __init__(self):
        super(PoolSidePlayer, self).__init__()

        self.pss = PoolSideStream()

        self.p = None

        self.initUI()

    def play(self):
        if self.pss.get_state() == gst.STATE_PLAYING:
            self.pss.pause()
        elif self.pss.get_state() == gst.STATE_PAUSED:
            self.pss.play()
        else:
            thread.start_new_thread(self.pss.play_tracks, ())
            gobject.threads_init()
            loop = glib.MainLoop()
            loop.run()

            # self.p = Process(target=self.pss.play_tracks)
            # self.p.start()
            # self.p.join()

    def skip(self):
        # self.p.terminate()
        self.pss.stop()
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

    def cleanUp(self):
        del self.pss
        self.loop.quit()
        thread.exit()

    def closeEvent(self, QCloseEvent):
        self.cleanUp()

    def __del__(self):
        self.cleanUp()

def main():

    app = QtGui.QApplication(sys.argv)
    ex = PoolSidePlayer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()