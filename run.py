#!/usr/bin/python

import subprocess
import os
import re
import signal
import time

#auto_start = None
auto_start = 'KEY_1'

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

def visualization_start():
	proc = subprocess.Popen(['projectM-pulseaudio'], shell=False, preexec_fn=os.setsid)
	# Maximize by sending 'f' key to the app (its Fullscreen setting in .projectM/config.inp didn't work)
	time.sleep(1)
	os.system("xdotool search --name projectM key f")
	return proc

def visualization_stop(visu_ctx):
	visu_ctx.kill()
	visu_ctx.terminate()

def shutdown_start():
	os.system("systemctl poweroff")

class mpd_ctx:
	def __init__(self):
		self.mpd_ctx = None
		self.visu_ctx = None

def mpd_stop(ctx):
	visualization_stop(ctx.visu_ctx)
	subprocess.Popen('killall mpd', shell=True)
	ctx.mpd_ctx.kill()
	ctx.mpd_ctx.terminate()
	ctx.visu_ctx = None
	dpms(1)

def mpd_start():
	dpms(0)
	ctx = mpd_ctx()
	ctx.mpd_ctx = subprocess.Popen(['mpd'], shell=False, preexec_fn=os.setsid)
	ctx.visu_ctx = visualization_start()
	print("MPD ctx", ctx)
	return ctx

def kodi_start():
	irw_stop()
	os.system("kodi")
	irw_run()

actions = dict()

actions['KEY_1'] = [ "MPD", mpd_start, mpd_stop ]
actions['KEY_2'] = [ "Kodi", kodi_start, None ]
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
