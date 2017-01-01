#!/bin/sh

userresources=$HOME/.Xresources
usermodmap=$HOME/.Xmodmap
sysresources=/etc/X11/xinit/.Xresources
sysmodmap=/etc/X11/xinit/.Xmodmap

# merge in defaults and keymaps

if [ -f $sysresources ]; then
    xrdb -merge $sysresources
fi

if [ -f $sysmodmap ]; then
    xmodmap $sysmodmap
fi

if [ -f "$userresources" ]; then
    xrdb -merge "$userresources"
fi

if [ -f "$usermodmap" ]; then
    xmodmap "$usermodmap"
fi

# start some nice programs

if [ -d /etc/X11/xinit/xinitrc.d ] ; then
 for f in /etc/X11/xinit/xinitrc.d/?*.sh ; do
  [ -x "$f" ] && . "$f"
 done
 unset f
fi

# Set ALSA volume in case we want to play MAME, etc.
amixer sset Master unmute

pulseaudio --start

#This is needed so Kodi can do Shutdown, Supend
/usr/bin/dbus-daemon --session --address=systemd: --nofork --nopidfile --systemd-activation &
/usr/lib/polkit-1/polkitd --no-debug &

# Run in foreground, so we don't run the window manager unless user exits Kodi
#kodi
#./run.py

# If Kodi exits, Now switch to desktop mode with a window manager
exec awesome
