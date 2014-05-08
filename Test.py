import soundcloud
import pygst
import gst
# from kivy.core.audio import SoundLoader

def test1():
    # Create a new client that uses the user credentials oauth flow
    client = soundcloud.Client(
        client_id='e72237107739281ffceb867534efd87c',
        client_secret='8cabee4b329b64ef593c6dce38ebe1ad',
        username='uname',
        password='password'
    )

    # print the username of the authorized user
    print client.get('/me').username

def test2():
    # create a client object with your app credentials
    client = soundcloud.Client(client_id='e72237107739281ffceb867534efd87c')

    # fetch track to stream
    track = client.get('/tracks/293')

    # get the tracks streaming URL
    stream_url = client.get(track.stream_url, allow_redirects=False)

    # print the tracks stream URL
    print stream_url.location

def test3():
    def on_tag(bus, msg):
        taglist = msg.parse_tag()
        print 'on_tag:'
        for key in taglist.keys():
            print '\t%s = %s' % (key, taglist[key])

    #our stream to play
    #http://api.soundcloud.com/tracks/{id}/stream?client_id=YOUR_CLIENT_ID
    music_stream_uri = 'http://api.soundcloud.com/tracks/105086121/stream?client_id=e72237107739281ffceb867534efd87c'

    #creates a playbin (plays media form an uri)
    player = gst.element_factory_make("playbin", "player")

    #set the uri
    player.set_property('uri', music_stream_uri)

    #start playing
    player.set_state(gst.STATE_PLAYING)

    #listen for tags on the message bus; tag event might be called more than once
    bus = player.get_bus()
    bus.enable_sync_message_emission()
    bus.add_signal_watch()
    bus.connect('message::tag', on_tag)

    #wait and let the music play
    raw_input('Press enter to stop playing...')

test3()