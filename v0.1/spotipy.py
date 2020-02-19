# Spotipy v0.1
# Author: Sam Bowyer
# Basic script to get stats on spotify playlists
# (mainly for my 'post' playlists)

#TODO:
#  - read targetPlaylistNames from a text file instead of defining here
#  - have a separate script for downloading the necessary JSON objects so that this file can just be
#    for statistical analysis/UI (and we don't have to do lots of curl calls/token gets)
#  - implement UI


import subprocess #used to run command line operations to get json objects from the spotify api
import json
import requests #https://curl.trillworks.com/#python converts curl to python
import webbrowser

def msToHumanTime(ms, day=False):
    hours = int(ms / (60*60*1000))
    minutes = int(ms / (60*1000)) % (60)
    seconds = int((ms / 1000)) % (60)
    result = ""
    if day:
        hours = hours % 24
        days = int(ms / (60*60*1000*24))

    for t in [[hours, "h"], [minutes, "m"], [seconds, "s"]]:
        result += (str(t[0]) + t[1]).ljust(4)

    if day:
        result = (str(days)+"d").ljust(4) + result

    return result[:len(result)-1]

if input("Open web browser to get token? (y/n): ") == "y":
    webbrowser.open("https://developer.spotify.com/console/get-current-user-playlists/?limit=&offset=")
token = input("token: ")

userID = "116138018"
#token = 'BQAzryJYszF2E8DSG6umLqjcV3pYXGZy76eOGHl2z1ZmUndmIWJkNfBD-GDZ2LH29MJSJ86bZDfhS4onCKpc4tTEQdLl-QDs5yeBKRtb3tHcS9tPBmJxBkL56AaHdhQnikRBmEZUMOHh4H7MGQKYlSNYEnYV8A'

targetPlaylistNames = ["post melon", "roast malone", "toast malone", "ghost malone",
                       "ho-ho-ho malone",
                       "post trombone", "sylvester malone",
                       "post flinstone", "poached malone", "post well-known",
                       "post shalom", "Victor Gluten"]

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+ token,
}
params = (
    ('limit', '100'),
)

# only gets the first 20 playlists - need to make sure the target playlists are all in this first 20
# otherwise we will have to use responseJSON["next"] to get the URL for the next 20 playlistIDs
# or call request.get() with the param offset=20 a total number of **(responseJSON["total"]/20)** number of times
response = requests.get('https://api.spotify.com/v1/users/116138018/playlists', headers=headers)
responseJSON = response.json()
playlists = responseJSON["items"]

#get the URLs and lengths used for each of the target playlists for future
targetPlaylists = []

for playlist in playlists:
    if playlist["name"] in targetPlaylistNames:
        targetPlaylists.append(playlist)

albumNames = []
albumYears = {}
albumsPerPlaylist = {}
tracksPerPlaylist = {}
durationPerPlaylist = {}

for playlist in targetPlaylistNames:
    durationPerPlaylist[playlist] = 0

for i, playlist in enumerate(targetPlaylists):
    tempTracksURL = playlist["tracks"]["href"]
    tempPlaylistLength = playlist["tracks"]["total"]

    print((playlist["name"] + ": ").ljust(18), end="")

    for offset in range(0, tempPlaylistLength, 100):
        response = requests.get(tempTracksURL+"?fields=items(added_at%2Ctrack(duration_ms%2Calbum(name%2Crelease_date)))&limit=100&offset="+str(offset), headers=headers)
        tempTracksJSON = response.json()["items"]

        # if playlist["name"] in albumsPerPlaylist:
        #     tracksPerPlaylist[playlist["name"]] += tempPlaylistLength
        # else:
        #     albumsPerPlaylist[playlist["name"]] = tempPlaylistLength

        for tempTracks in tempTracksJSON:
            #print(tempTracks)

            durationPerPlaylist[playlist["name"]] += tempTracks["track"]["duration_ms"]

            if tempTracks["track"]["album"]["name"] not in albumNames:
                albumNames.append(tempTracks["track"]["album"]["name"])
                if tempTracks["track"]["album"]["release_date"][:4] in albumYears:
                    albumYears[tempTracks["track"]["album"]["release_date"][:4]] += 1
                else:
                    albumYears[tempTracks["track"]["album"]["release_date"][:4]] = 1

                if playlist["name"] in albumsPerPlaylist:
                    albumsPerPlaylist[playlist["name"]] += 1
                else:
                    albumsPerPlaylist[playlist["name"]] = 1

        print("+", end="")
    print()

max = 0
totalTracks = 0
totalTime = 0

for year in albumYears:
    if albumYears[year] > max:
        max = albumYears[year]
    totalTracks += albumYears[year]

for playlist in durationPerPlaylist:
    totalTime += durationPerPlaylist[playlist]

def terminal_width():
    import fcntl, termios, struct
    th, tw, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return tw

for year in sorted(albumYears):

    plusNo = int(round(albumYears[year]*(terminal_width()-10)/max))
    #if plusNo == 0:
    #    plusNo = 1
    print(year + ": " + str(albumYears[year]).ljust(3) +" " + "+"*plusNo)

print("\nAlbums per playlist")
for playlist in targetPlaylists:
    print(playlist["name"].ljust(16) + ": " + str(albumsPerPlaylist[playlist["name"]]).ljust(3)
          + " (" + str(playlist["tracks"]["total"]).ljust(4) + " tracks, "
          + msToHumanTime(durationPerPlaylist[playlist["name"]]) + ")")

print("\nTotal: " + str(totalTracks) + " tracks, " + msToHumanTime(totalTime, day=True))
