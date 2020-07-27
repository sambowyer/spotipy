# Spotipy v0.2 client
# Author: Sam Bowyer
# Terminal client for app to get stats on spotify playlists
# (mainly for my 'post' playlists)

#TODO: - Implement stats using local JSON files rather than using requests as in v0.1

import subprocess #used to run command line operations to get json objects from the spotify api
import json
import requests #https://curl.trillworks.com/#python converts curl to python
import webbrowser
import time

print("############### Spotipy v0.2.1 ###############")

f = open("data.txt", "r")
lastJSONUpdate = f.read().strip()
f.close()

def terminal_width():
    import fcntl, termios, struct
    th, tw, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return tw

def stats():
    targetPlaylistNames = readTargetPlaylists("targetPlaylists.txt")
    targetPlaylists = []
    with open("playlists.json", "r") as f:
        playlists = json.load(f)["items"]

    for playlist in playlists:
        if playlist["name"] in targetPlaylistNames:
            targetPlaylists.append(playlist)

    print(targetPlaylists)

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

        print((playlist["name"] + ": ").ljust(18), end="\n")

        for offset in range(0, tempPlaylistLength, 100):
            #response = requests.get(tempTracksURL+"?fields=items(added_at%2Ctrack(duration_ms%2Calbum(name%2Crelease_date)))&limit=100&offset="+str(offset), headers=headers)
            with open("JSON/"+playlist["name"]+ "_" + str(int(offset/100)), "r") as f:
                tempTracksJSON = json.load(f)["items"]

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

    print("\nTotal: " + str(totalTracks) + " albums, " + msToHumanTime(totalTime, day=True))

    max = 0
    totalTracks = 0
    totalTime = 0

    for year in albumYears:
        if albumYears[year] > max:
            max = albumYears[year]
        totalTracks += albumYears[year]

    for year in sorted(albumYears):

        plusNo = int(round(albumYears[year]*(terminal_width()-10)/max))
        #if plusNo == 0:
        #    plusNo = 1
        print(year + ": " + str(albumYears[year]).ljust(3) +" " + "+"*plusNo)

def updateJSON():
    userID = "116138018"
    targetPlaylistNames = readTargetPlaylists("targetPlaylists.txt")

    maxPlaylistNameLength = max([len(x) for x in targetPlaylistNames])

    if input("Open web browser to get token? (y/n): ") == "y":
        webbrowser.open("https://developer.spotify.com/console/get-current-user-playlists/?limit=&offset=")

    token = input("token: ")

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ token,
    }

    try:
        with open("playlists.csv", "w") as f:
            while len(targetPlaylistNames) != 0:
                response = requests.get(url + 'fields=items(name%2Ctracks(href%2Ctotal))%2Cnext', headers=headers)
                responseJSON = response.json()
                for playlist in responseJSON["items"]:
                    if playlist["name"] in targetPlaylistNames:
                        f.write(playlist["name"] + "," + str(playlist["tracks"]["total"]) + "," + playlist["tracks"]["href"] + "\n")
                        targetPlaylistNames.remove(playlist["name"])
                url = responseJSON["next"] + "&"
                if url == "null&":
                    print("The following playlists were not found: " + targetPlaylistNames)
                    break
    except:
        print("Error in JSON download. Probably due to an expired token.\n")
        return

    #get the URLs and lengths used for each of the target playlists for future
    targetPlaylists = []
    with open("playlists.csv", "r") as f:
        targetPlaylists = [x.split(",") for x in f.readlines()]

    for playlist in targetPlaylists:
        tempPlaylistName = playlist[0]
        tempPlaylistLength = int(playlist[1])
        tempTracksURL = playlist[2].strip()

        print((tempPlaylistName + ": ").ljust(maxPlaylistNameLength+2), end="")
        # print(tempTracksURL)

        for offset in range(0, tempPlaylistLength, 100):
            response = requests.get(tempTracksURL+"?fields=items(added_at%2Ctrack(duration_ms%2Calbum(name%2Crelease_date)))&limit=100&offset="+str(offset), headers=headers)
            # print(response.status_code)
            # print(response.url)

            with open("JSON/" + tempPlaylistName + "_" + str(int(offset/100)), "w+") as f:
                f.write(response.text)

            print("+", end="")
        print()

    with open("data.txt", "w") as f:
        f.write(time.ctime())
    f = open("data.txt", "r")
    lastJSONUpdate = f.read().strip()
    f.close()
    print("Update done.\n")



def readTargetPlaylists(file):
    with open(file, "r") as f:
        return f.read().splitlines();

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

menuText = """Pick an option:

    [0] Get stats
    [1] Edit target playlists
    [2] Update JSON files (last edited %s)
    [3] Exit """ % (lastJSONUpdate)

menu = ""

print(menuText)

while menu not in [str(n) for n in range(4)]:
    menu = input(">>>  ")

    if menu == "0":
        stats()

    elif menu == "1":
        subprocess.run(["open", "targetPlaylists.txt"])

    elif menu == "2":
        updateJSON()

    elif menu == "3":
        break

    menu = ""
    print(menuText)
