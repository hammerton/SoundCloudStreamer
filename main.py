import sys
import gst
import urllib2
import ast
import random
from PyQt4 import QtGui

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

        #creates a playbin (plays media form an uri)
        self.player = gst.element_factory_make("playbin", "player")

        self.initUI()

    @staticmethod
    def get_all_tracks():
        response = urllib2.urlopen("http://poolsideapi2.herokuapp.com/tracks")
        tracks = ast.literal_eval(response.read())
        return tracks

    def get_random_track(self):
        return random.choice(self.tracks)

    def play_track(self):
        curr_track = self.get_random_track()

        #our stream to play
        #http://api.soundcloud.com/tracks/{id}/stream?client_id={YOUR_CLIENT_ID}
        music_stream_uri = 'http://api.soundcloud.com/tracks/%s/stream?client_id=e72237107739281ffceb867534efd87c' \
                           % curr_track['scId']

        #set the uri
        self.player.set_property('uri', music_stream_uri)

        #start playing
        self.player.set_state(gst.STATE_PLAYING)

    def play(self):
        if self.player.get_state()[1] == gst.STATE_PLAYING:
            self.player.set_state(gst.STATE_PAUSED)
        elif self.player.get_state()[1] == gst.STATE_PAUSED:
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.play_track()

    def skip(self):
        self.player.set_state(gst.STATE_NULL)
        self.play_track()

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