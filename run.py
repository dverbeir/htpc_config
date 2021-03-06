#!/usr/bin/python

import subprocess
import os
import re
import signal
import time

auto_start = None
#auto_start = 'KEY_1'

default_audio_profile = "output:hdmi-surround"
debounce = 2;
pattern = re.compile("\S+\s+(\d+)\s+(\S+)")

# Because screen blank in HDMI also turns off audio :-(
def dpms(state):
	if state:
		os.system("xset +dpms")
	else:
		os.system("xset s 0 0")
		os.system("xset dpms 0 0 0")
		os.system("xset s off")

def shutdown_start():
	os.system("systemctl poweroff")

def pulse_set_profile(audio_profile):
	subprocess.Popen('pactl set-card-profile 0 '+audio_profile, shell=True)

def mpd_start():
	dpms(0)
	irw_stop()
	pulse_set_profile(default_audio_profile)
	os.system("./run_mpd.py")
	dpms(1)
	irw_run()

def kodi_start():
	irw_stop()
	os.system("bash -c \"sleep 2; xdotool search --name kodi key super+f\" &")
	os.system("kodi")
	irw_run()

def n64_start():
	irw_stop()
	os.system("emulationstation")
	irw_run()

actions = dict()

actions['KEY_1'] = [ "MPD", mpd_start, None ]
actions['KEY_2'] = [ "Kodi", kodi_start, None ]
actions['KEY_3'] = [ "MUPEN64PLUS", n64_start, None ]
#actions['KEY_4'] = [ "MPD Zone2", lambda: mpd_start("output:analog-stereo"), mpd_stop ]
actions['KEY_0'] = [ "System Shutdown", shutdown_start, None ]


irw_proc = None
cur = None
cur_ctx = None

def menu():
	global actions
	for k in actions.keys():
		print(k, ": ", actions[k][0])

def start_activity():
	global cur_ctx
	print("Starting ", cur[0])
	print("XDG_RUNTIME_DIR="+os.environ['XDG_RUNTIME_DIR'])
	cur_ctx = cur[1]()

def stop_activity():
	global cur, cur_ctx
	if cur:
		print("Stopping ", cur[0])
		if cur[2]:
			cur[2](cur_ctx)

def irw_run():
	global irw_proc
	irw_proc = subprocess.Popen(['irw'], stdout=subprocess.PIPE)

def irw_stop():
	global irw_proc
	irw_proc.kill()
	irw_proc.terminate()
	irw_proc.wait()
	irw_proc = None

irw_run()

if auto_start:
	cur = actions[auto_start]
	start_activity()

while True:
	menu()

	line = irw_proc.stdout.readline()
	if line == '' and irw_proc.poll() != None:
       		break
	#print(line)
	s = line.decode("utf-8")
	print(s)

	match = pattern.match(s)
	if int(match.group(1)) == debounce:
		key = match.group(2)

		#print("Trigger: ", key)
		if key == "KEY_STOP":
			stop_activity()
			cur = None

		elif key in actions.keys():
			stop_activity()
			cur = actions[key]
			start_activity()
