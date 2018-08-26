#!/usr/bin/python

import os
import subprocess

cur_playlist_fn = "/tmp/mpd_cur_playlist"

def mpc_seek(seek_val):
    os.system("mpc seek " + seek_val)

def mpc_play():
    os.system("mpc play")

def mpc_pause():
    os.system("mpc pause")

def mpc_toggle():
    os.system("mpc toggle")

def mpc_next():
    os.system("mpc next")

def mpc_prev():
    os.system("mpc prev")

def mpc_volume(vol_change):
    os.system("mpc volume " + vol_change)

def mpc_change_playlist(delta):
    result = subprocess.run(['mpc', 'lsplaylists'], stdout=subprocess.PIPE)
    playlists = result.stdout.decode('utf-8').rstrip().split("\n")
    print(playlists)

    # Load current playlist number and move to next one
    cur_f = None
    try:
      cur_f = open(cur_playlist_fn, "r")
      val = int(cur_f.read())
      cur_f.close()
    except (FileNotFoundError, IOError):
      val = 0
    val += delta
    if val >= len(playlists):
      val = 0
    if val < 0:
      val = len(playlists) - 1
    print("val="+str(val))

    cur_f = open(cur_playlist_fn, "w")
    cur_f.write(str(val))
    cur_f.close()
    os.system("mpc clear")
    os.system("mpc load '" + playlists[val] + "'")
    os.system("mpc play")
