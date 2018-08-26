#!/usr/bin/python

import subprocess
import os
import re
import signal
import time
import mpd_control

default_audio_profile = "output:hdmi-surround"
debounce = 2;
pattern = re.compile("\S+\s+(\d+)\s+(\S+)")

irw_proc = None
visu_proc = None
cover_art_proc = None
audio_profile = default_audio_profile

def cover_art_start():
	global cover_art_proc

	cover_art_proc = subprocess.Popen(['bum', '--size', '800'], shell=False, preexec_fn=os.setsid)

def cover_art_stop():
	global cover_art_proc

	if cover_art_proc:
		cover_art_proc.kill()
		cover_art_proc.terminate()
		cover_art_proc = None

def cover_art_toggle():
	global cover_art_proc

	if cover_art_proc:
		cover_art_stop()
	else:
		cover_art_start()

def visualization_start():
	global visu_proc

	visu_proc = subprocess.Popen(['projectM-pulseaudio'], shell=False, preexec_fn=os.setsid)
	# Maximize by sending 'f' key to the app (its Fullscreen setting in .projectM/config.inp didn't work)
	time.sleep(1)
	os.system("xdotool search --name projectM key f")

def visualization_stop():
	global visu_proc

	if visu_proc:
		visu_proc.kill()
		visu_proc.terminate()
		visu_proc = None

def visualization_toggle():
	global visu_proc

	if visu_proc:
		visualization_stop()
	else:
		visualization_start()
		
def pulse_set_profile(audio_profile):
	print("MPD: audio_profile="+audio_profile)
	subprocess.Popen('pactl set-card-profile 0 '+audio_profile, shell=True)

def irw_run():
	global irw_proc

	irw_proc = subprocess.Popen(['irw'], stdout=subprocess.PIPE)

def irw_stop():
	global irw_proc

	irw_proc.kill()
	irw_proc.terminate()
	irw_proc.wait()
	irw_proc = None

def mpd_stop():
	global mpd_proc

	visualization_stop()
	subprocess.Popen('killall mpd', shell=True)
	mpd_proc.kill()
	mpd_proc.terminate()

	pulse_set_profile(default_audio_profile)

def mpd_start():
	global audio_profile
	global mpd_proc

	pulse_set_profile(audio_profile)
	mpd_proc = subprocess.Popen(['mpd'], shell=False, preexec_fn=os.setsid)

def mpd_exit():
	global leave

	leave = True


actions = dict()

actions['KEY_RED'] = lambda: pulse_set_profile("output:hdmi-surround")
actions['KEY_BLUE'] = lambda: pulse_set_profile("output:analog-stereo")

actions['KEY_NEXT'] = mpd_control.mpc_next
actions['KEY_PREVIOUS'] = mpd_control.mpc_prev
actions['KEY_PLAY'] = mpd_control.mpc_play
actions['KEY_PAUSE'] = mpd_control.mpc_pause
actions['KEY_FORWARD'] = lambda: mpd_control.mpc_seek("+5%")
actions['KEY_REWIND'] = lambda: mpd_control.mpc_seek("-5%")

actions['KEY_UP'] = lambda: mpd_control.mpc_change_playlist(+1)
actions['KEY_DOWN'] = lambda: mpd_control.mpc_change_playlist(-1)

actions['KEY_EPG'] = visualization_toggle
actions['KEY_INFO'] = cover_art_toggle

actions['KEY_EXIT'] = mpd_exit


leave = False

irw_run()
mpd_start()

while not leave:
	line = irw_proc.stdout.readline()
	if line == '' and irw_proc.poll() != None:
       		break
	#print(line)
	s = line.decode("utf-8")
	print(s)

	match = pattern.match(s)
	if int(match.group(1)) == debounce:
		key = match.group(2)

		print("Trigger: ", key)
		if key in actions.keys():
			actions[key]()

print("Out of loop")
mpd_stop()
irw_stop
