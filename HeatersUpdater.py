#!/usr/bin/env python

import spotipy, json
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timezone, timedelta

def GetAllPlaylistTracks(spotify, playlistId):
    playlist = spotify.playlist(playlist_id=playlistId)["tracks"]
    tracks = playlist["items"]

    while playlist["next"]:
        playlist = spotify.next(playlist)
        tracks.extend(playlist["items"])
    
    return tracks

def DeleteOldSongs(spotify, timeToCheck, secrets):
    heaters = GetAllPlaylistTracks(spotify, secrets["playlist_id"])

    songsToRemove = []
    names = []

    for song in heaters:
        ShowSongStats(song, timeToCheck)
        if datetime.fromisoformat(song["added_at"]).timestamp() < timeToCheck:
            songsToRemove.append(song["track"]["id"])
            names.append(song["track"]["name"])

    print("")
    print(f"{'':-<100}")
    print("")

    if(len(songsToRemove) != 0):
        print(f"Removing the following {len(songsToRemove)} songs:")
        for x in range(len(songsToRemove)):
            print(f"id: {songsToRemove[x]} | name: {names[x]}")
        
        print("\nDeleting...")
        spotify.playlist_remove_all_occurrences_of_items(playlist_id=secrets["playlist_id"], items=songsToRemove)
        print("Done!")
    else:
        print("No songs to delete :)")

def ShowSongStats(song, timeToCheck):
    timeLeft = timedelta(seconds=(datetime.fromisoformat(song["added_at"]).timestamp() - timeToCheck))
    print(f"{str(timeLeft.days) + ' days left':-<20}|{song['track']['name'].strip()}")

def AddNewSongs(ranscheiID, spotify: spotipy.Spotify, timeToCheck, secrets):
    sentinal = True
    startPoint = 100

    namesToAdd = []
    songsToAdd = []
    idsToAdd = []

    while sentinal:
        tempNamesToAdd = []
        tempSongsToAdd = []
        tempIdsToAdd = []

        offset = spotify.playlist(playlist_id=ranscheiID)["tracks"]["total"] - startPoint
        ranschei = spotify.playlist_items(playlist_id=ranscheiID, limit=100, offset=offset)
        if datetime.fromisoformat(ranschei["items"][0]["added_at"]).timestamp() >= timeToCheck:
            for song in ranschei["items"]:
                tempSongsToAdd.append(song["track"]["uri"])
                tempNamesToAdd.append(song["track"]["name"])
                tempIdsToAdd.append(song["track"]["id"])
            songsToAdd = tempSongsToAdd + songsToAdd
            namesToAdd = tempNamesToAdd + namesToAdd
            idsToAdd = tempIdsToAdd + idsToAdd
            startPoint += 100
        else:
            for song in ranschei["items"]:
                if datetime.fromisoformat(song["added_at"]).timestamp() >= timeToCheck:
                    tempSongsToAdd.append(song["track"]["uri"])
                    tempNamesToAdd.append(song["track"]["name"])
                    tempIdsToAdd.append(song["track"]["id"])
            songsToAdd = tempSongsToAdd + songsToAdd
            namesToAdd = tempNamesToAdd + namesToAdd
            idsToAdd = tempIdsToAdd + idsToAdd
            sentinal = False

    heaters = spotify.playlist(playlist_id=secrets["playlist_id"])

    preAddedSongs = []
    preAddedNames = []
    finalSongsToAdd = []
    finalNames = []

    for song in heaters["tracks"]["items"]:
        preAddedSongs.append(song["track"]["uri"])
        preAddedNames.append(song["track"]["name"])
    
    for ranSong in songsToAdd:
        if ranSong not in preAddedSongs not in finalSongsToAdd:
            finalSongsToAdd.append(ranSong)
    
    for ranName in namesToAdd:
        if ranName not in preAddedNames not in finalNames:
            finalNames.append(ranName)

    if len(finalSongsToAdd) > 0:
        print(f"Adding the following {len(finalSongsToAdd)} songs:")
        for x in range(len(finalSongsToAdd)):
            print(f"id: {finalSongsToAdd[x]} | name: {finalNames[x]}")

        print("\nAdding...")
        spotify.playlist_add_items(playlist_id=secrets["playlist_id"], items=finalSongsToAdd)
        print("Done!")
    else:
        print("No new songs to add :)")

def Main():
    secrets = json.load(open("D:\Programmering\Github\SpotifyHeatersUpdater\Secrets.json"))
    ranscheiID = secrets["ranschei_id"]

    scope = "playlist-modify-public"

    authManager = SpotifyOAuth(client_id=secrets["client_id"], client_secret=secrets["client_secret"], scope=scope, redirect_uri="http://localhost/")
    spotify  = spotipy.Spotify(auth_manager=authManager)

    timeToCheck = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()

    DeleteOldSongs(spotify, timeToCheck, secrets)

    AddNewSongs(ranscheiID, spotify, timeToCheck, secrets)

    input()

if __name__ == '__main__':
    Main()