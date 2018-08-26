# Introduction

These files and scripts are meant to configure an HTPC system so that it can run alternative applications under control of the IR remote control.
This was installed on Arch Linux.

Applications currently controlled:
* MPD (to play audio, controlled using the IR remote, or natively also from Smartphone/tablet/...)
  * With visualization effects using ProjectM
  * with album cover art display using `bum`
* Kodi for video
* System shutdown

The run.py script allows configuration an app to automatically start (MPD in my case). Pressing '2' on the IR remote then allows to switch to Kodi. When exiting from Kodi, you get back to the IR controller menu, from which MPD can be started again or the system can be shut down.
