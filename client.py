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

print("############### Spotipy v0.2 ###############")

f = open("data.txt", "r")
lastJSONUpdate = f.read().strip()
f.close()

def stats():
    pass

def updateJSON():
    userID = "116138018"
    targetPlaylistNames = readTargetPlaylists("targetPlaylists.txt")

    if input("Open web browser to get token? (y/n): ") == "y":
        webbrowser.open("https://developer.spotify.com/console/get-current-user-playlists/?limit=&offset=")

    token = input("token: ")

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ token,
    }
    params = (
        ('limit', '100'),
    )

    # TODO: only gets the first 20 playlists - need to make sure the target playlists are all in this first 20
    # otherwise we will have to use responseJSON["next"] to get the URL for the next 20 playlistIDs
    # or call request.get() with the param offset=20 a total number of **(responseJSON["total"]/20)** number of times
    response = requests.get('https://api.spotify.com/v1/users/116138018/playlists', headers=headers)
    responseJSON = response.json()

    with open("playlists.json", "w+") as f:
        f.write(response.text)

    try:
        playlists = responseJSON["items"]
    except:
        print("Error in JSON download. Probably due to an expired token.\n")
        return

    #get the URLs and lengths used for each of the target playlists for future
    targetPlaylists = []

    for playlist in playlists:
        if playlist["name"] in targetPlaylistNames:
            targetPlaylists.append(playlist)

    for i, playlist in enumerate(targetPlaylists):
        tempTracksURL = playlist["tracks"]["href"]
        tempPlaylistLength = playlist["tracks"]["total"]

        print((playlist["name"] + ": ").ljust(18), end="")

        for offset in range(0, tempPlaylistLength, 100):
            response = requests.get(tempTracksURL+"?fields=items(added_at%2Ctrack(duration_ms%2Calbum(name%2Crelease_date)))&limit=100&offset="+str(offset), headers=headers)

            with open("JSON/" + playlist["name"] + "_" + str(int(offset/100)), "w+") as f:
                f.write(response.text)

            print("+", end="")
        print()

    with open("data.txt", "w") as f:
        f.write(time.ctime())
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