import httplib
import json
import cherrypy
import thread
import urllib
import actions
import pytify
import os


class SpotifyPlayer:
    def __init__(self):
        self.spotify = pytify.Spotify()

    def play_spotify_uri_handler(self, value):
        spotifyuri = value.get("spotify_uri")
        if spotifyuri:
            os.startfile(spotifyuri)
            if spotifyuri.startswith("spotify:album:"):
                self.spotify.next()  # this is needed to make
                self.spotify.previous()  # albums autoplay
        return spotifyuri

    def handlers(self):
        return [self.play_spotify_uri_handler]

    def actions(self):
        return [
            actions.Action("Stop", "stop", self.spotify.stop),
            actions.Action("Pause", "pause", self.spotify.playpause),
            actions.Action("Next", "next", self.spotify.next),
            actions.Action("Previous", "previous", self.spotify.previous)]


class SpotifyApi:
    def __init__(self):
        pass

    def urilookup(self, uri):
        return self.request("lookup", "", uri=uri)

    def track_search(self, text):
        if text != "":
            for track in self.request("search", "track", q=text)["tracks"]:
                uri = track["href"]
                name = track["name"]
                artist = track["artists"][0]["name"]
                value = {"spotify_uri": uri, "artist": artist, "track_name": name}
                yield (value, name, name + " [" + artist + "]")

    def request(self, service, path, **params):
        connection = httplib.HTTPConnection("ws.spotify.com")
        url = "/" + service + "/1/" + path + ".json" + "?" + "".join(
            ["&" + name + "=" + str(value).replace(" ", "+") for name, value in params.items()])
        print ( url )
        connection.request("GET", url)
        response = connection.getresponse()
        data = response.read()
        j = json.loads(data)
        connection.close()
        return j


class Entry:
    def __init__(self):
        pass


class SpotifySearchPage:
    def __init__(self, context, spotifyapi):
        self.context = context
        self.spotifyapi = spotifyapi

    @cherrypy.expose
    def index(self, search=""):
        uri = None
        tracks = None
        if search.startswith("spotify:track"):
            cleanuri = search
            starttime = ""
            hash = cleanuri.find("#")
            if hash != -1:
                cleanuri = search[:hash]
                starttime = search[hash + 1:]
            track = self.spotifyapi.urilookup(cleanuri)["track"]
            name = track["name"]
            artist = track["artists"][0]["name"]
            uri = Entry()
            uri.value = {"spotify_uri": search, "artist": artist, "track_name": name}
            uri.name = name
            uri.longname = name + " [" + artist + "] " + starttime
        else:
            tracks = self.spotifyapi.track_search(search)
        return self.context.render("spotify.html", "Spotify", search=search, uri=uri, tracks=tracks)

