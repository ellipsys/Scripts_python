#!/usr/bin/python
## lk_beam_finder.py : i
##	A tool for automatically point an antena to a WiFi AP or client
##
### IMPORTS SECTION
###
#import serial
#import time
import sys
#from datetime import datetime
#import re
#import os
#import resource
#import platform
import argparse
#import fcntl, termios, struct
import lk_servo_system
# Import scapy while ignoring warnings (to avoid annoying warning msg about ipv6)
tmpout = sys.stdout; tmperr = sys.stderr
sys.stdout = open('/dev/null', 'w'); sys.stderr = open('/dev/null', 'w')
from scapy.all import *
sys.stdout = tmpout; sys.stderr = tmperr
# Import scapy while ignoring warnings (to avoid annoying warning msg about ipv6)
from threading import Thread
import mutex
from threading import Lock
import lk_servo_system
from lk_screen_log import lkScreenMsg

###
### FUNCTION SECTION
###
# create_argumentparser :       Creates the argument parser for this program
def create_argumentparser():
	desc =  'lk_beam_finder.py (v1.0) - Wi-Fi beam direction finding tool\n'
	desc += 'Copyright (c) 2015 Layakk (www.layakk.com) (@layakk)'

	parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
	parser.add_argument("-c", "--config_file", help="File containing the configuration of the servo system managed by one microcontroller. If you don't specify this file, the lk_servo_system.py library will choose the one in the default location (/etc/lk_servo_system.conf)", type=str, required=False)
	parser.add_argument("-i", "--interface", help='WiFi interface to listen on (must alread be up and in monitor mode)', required=True)
	parser.add_argument("-s", "--station", help='Pan-Tilt Station where the antenna is attached. This value can be the station label or the station number', type=str, required=True)
	parser.add_argument("-t", "--measure_time", help='Time to spend measuring in each station position (float, secs). Default=2', type=float, required=False)
	parser.add_argument("-g", "--grid_size", help='Number of points that the search grid will have in each dimension. [3..9]. Default=6', type=int, required=False, default=6)
	parser.add_argument("-l", "--speed_limit", help='Pulse variation speed limit for servo motors, in 0.25 usec / 10 msec. (0=nolimit, min=1, max=64). If not specified, the system will set the safe value from the config file.', type=int, required=False, default=-1)
	parser.add_argument("-p", "--pan_limits", help="Pan limits of operation 'min,max' (degrees). Default=max=15,170", type=str, required=False)
	parser.add_argument("-q", "--tilt_limits", help="Tilt limits of operation 'min,max' (degrees). Default=max=15,170", type=str, required=False)
	parser_mode_group = parser.add_mutually_exclusive_group(required=True)
	parser_mode_group.add_argument("-m", "--mac", help='MAC of the Wi-Fi device you are looking for', required=False)
	parser_mode_group.add_argument("-e", "--essid", help='ESSID of the Wi-Fi network you are looking for', required=False)
	parser.add_argument("-d", "--debug_mode", help="This options enables debug mode. In debug mode system will stop each time a loop iteration is finished.", required=False, action="store_true")
	return parser

def sniffcb_ap(p):
	global target_mac
	global target_essid
	global current_power_sum
	global current_power_max
	global current_power_sum_pos
	global current_power_count
	global pow_floor
	global pow_mutex
	global beacon_interval
	
	_is_target_frame = False
	_dot11 = None

	# Note:
	#     addr1 = receiver
	#     addr2 = transmitter
	#     addr3 = either original source or intended destination
	#     addr4 = original source when frame is both tx and rx on a wireless DS

	# Determine if this frame is of our interest
	if not p.haslayer(Dot11):
		return
	if not p.haslayer(Dot11Beacon):
		return
	_dot11Beacon = p.getlayer(Dot11Beacon)

	if target_mac is not None:
		if p[Dot11].addr2 == target_mac:
			_is_target_frame = True
	else:
		try:
			if _dot11Beacon.info == target_essid:
				_is_target_frame = True
		except AttributeError:
			pass

	if not _is_target_frame:
		return

	# Calculate beacon_interval for the first time
	if beacon_interval is None:
		try:
			beacon_interval = _dot11Beacon.beacon_interval
			return
		except AttributeError:
			return
			
	# Update global values
	_power = -(256-ord(p.notdecoded[-4:-3]))

	pow_mutex.acquire()
	if _power > current_power_max:
		current_power_max = _power
	current_power_sum += _power
	current_power_sum_pos += (_power - pow_floor)
	current_power_count += 1
	pow_mutex.release()
	

def reset_sniff_counters():
	global current_power_sum
	global current_power_sum_pos
	global current_power_count
	global current_power_max
	global pow_mutex

	pow_mutex.acquire()
	current_power_sum = 0
	current_power_max = -200
	current_power_sum_pos = 0
	current_power_count = 0
	pow_mutex.release()

def sniff_envelope():
	global interface
	global sniffcb_ap

	sniff(iface=interface, prn=sniffcb_ap, store=0)

def is_this_measure_better():
	if current_power_count < 0.5*best_powercount:
		return False
	if here_power_avg > best_poweravg:
		return True
	elif here_power_avg == best_poweravg and current_power_max > best_powermax:
		return True
	elif here_power_avg == best_poweravg and current_power_max == best_powermax:
		if current_power_count > best_powercount*2:
			return True
		else:
			return None
	else:
		return False

###
### GLOBAL VARIABLE SECTION
###
servosystem_limits = None
lastTiltAngle = 90
lastPanAngle = 90

beacon_interval = None
measure_time = 0
MIN_BEACONS_PER_MT = 10
current_power_sum = 0
current_power_max = -200
current_power_sum_pos = 0
current_power_count = 0
measure_time = 0.0
pow_mutes = None
pow_hyst_dbm = 4
angle_hyst = 10
pow_floor = -110
pow_mutex = Lock()

interface = None
target_mac = None
target_essid = None

pan_user_limits = None
tilt_user_limits = None
pan_low = None
pan_high = None
tilt_low = None
tilt_high = None
pan_range = None
tilt_range = None

arg_parser = None
arguments = None
SSystem = None

thread_sniff = None

best_powersumpos = -200
best_powercount = 0
best_poweravg = -200
best_powermax = -200
best_pan = None
best_tilt = None
ngrid = None

###
### MAIN
###
arg_parser = create_argumentparser()
arguments = arg_parser.parse_args()

lkScreenMsg("lk_beam_finder.py (v1.0) - Wi-Fi beam direction finding tool")
lkScreenMsg("Copyright (c) 2015 Layakk (www.layakk.com) (@layakk)")
lkScreenMsg()

lkScreenMsg("___ INITIALIZATION ___", IndentLevel=0)
lkScreenMsg("Initializing servo system...",IndentLevel=1)
if arguments.config_file:
	lkScreenMsg("(config file is %s)\t" % arguments.config_file, ToBeContinued=True, IndentLevel=2)
else:
	lkScreenMsg("(config file is the default one)", IndentLevel=2)
if arguments.config_file:
        SSystem=lk_servo_system.lkServoSystem(arguments.config_file)
else:
        SSystem=lk_servo_system.lkServoSystem()

if SSystem.errCondition:
        lkScreenMsg(" FAILED!")
        lkScreenMsg("(%s)" % SSystem.lastError, IndentLevel=3)
        lkScreenMsg("Exiting.", IndentLevel=2)
        SSystem.Close()
        exit(1)
else:
	lkScreenMsg(" OK!")

lkScreenMsg("Verifying command line...", ToBeContinued=True, IndentLevel=1)
interface = arguments.interface
if arguments.mac is not None:
	target_mac = arguments.mac.lower()
else:
	target_essid = arguments.essid
# Check correction of antenna number value
_auxmatch = re.match('\d+$',arguments.station)
if _auxmatch:
        station = int(_auxmatch.group())
else:
        station = SSystem.GetStationNumber(arguments.station)
if station == -1:
        lkScreenMsg(" FAILED!")
        lkScreenMsg("(%s)" % SSystem.lastError, IndentLevel=2)
        lkScreenMsg("Exiting.", IndentLevel=1)
        SSystem.Close()
        exit(1)
# Check correction of grid size.
if arguments.grid_size < 3 or arguments.grid_size > 9:
        lkScreenMsg(" FAILED!")
	lkScreenMsg("Grid size must be in the interval [3..9].", IndentLevel=2)
        lkScreenMsg("Exiting.", IndentLevel=1)
        SSystem.Close()
	exit(1)
ngrid = arguments.grid_size
# Check correction of pan and tilt limits
servosystem_limits = SSystem.GetStationLimits(station)
if arguments.pan_limits is not None or arguments.tilt_limits is not None:
	if arguments.pan_limits is not None:
		pan_user_limits = arguments.pan_limits.split(",")
		if len(pan_user_limits) != 2:
        		lkScreenMsg(" FAILED!")
			lkScreenMsg("pan_limits must be a list of exactly 2 values, separated by comma.", IndentLevel=2)
        		lkScreenMsg("Exiting.", IndentLevel=1)
        		SSystem.Close()
			exit(1)
		try:
			_tmp_low=int(pan_user_limits[0])
			_tmp_high=int(pan_user_limits[1])
		except ValueError:
        		lkScreenMsg(" FAILED!")
			lkScreenMsg("pan_limits must be integers between {low} and {high}".format(low=SC.getPanLowAngle(), high=SC.getPanHighAngle()), IndentLevel=2)
        		lkScreenMsg("Exiting.", IndentLevel=1)
        		SSystem.Close()
			exit(1)
		if _tmp_low < servosystem_limits[0][0] or _tmp_high > servosystem_limits[0][1]:
        		lkScreenMsg(" FAILED!")
			lkScreenMsg("pan_limits must be integers between {low} and {high}".format(low=SC.getPanLowAngle(), high=SC.getPanHighAngle()), IndentLevel=2)
        		lkScreenMsg("Exiting.", IndentLevel=1)
        		SSystem.Close()
			exit(1)
		pan_low = _tmp_low
		pan_high = _tmp_high
	else:
		pan_low = servosystem_limits[0][0]
		pan_high = servosystem_limits[0][1]
	if arguments.tilt_limits is not None:
		tilt_user_limits = arguments.tilt_limits.split(",")
		if len(tilt_user_limits) != 2:
        		lkScreenMsg(" FAILED!")
			lkScreenMsg("tilt_limits must be a list of exactly 2 values, separated by comma.", IndentLevel=2)
        		lkScreenMsg("Exiting.", IndentLevel=1)
        		SSystem.Close()
			exit(1)
		try:
			_tmp_low=int(tilt_user_limits[0])
			_tmp_high=int(tilt_user_limits[1])
		except ValueError:
        		lkScreenMsg(" FAILED!")
			lkScreenMsg("tilt_limits must be integers between {low} and {high}".format(low=SC.getPanLowAngle(), high=SC.getPanHighAngle()), IndentLevel=2)
        		lkScreenMsg("Exiting.", IndentLevel=1)
        		SSystem.Close()
			exit(1)
		if _tmp_low < servosystem_limits[1][0] or _tmp_high > servosystem_limits[1][1]:
        		lkScreenMsg(" FAILED!")
			lkScreenMsg("tilt_limits must be integers between {low} and {high}".format(low=SC.getPanLowAngle(), high=SC.getPanHighAngle()), IndentLevel=2)
        		lkScreenMsg("Exiting.", IndentLevel=1)
        		SSystem.Close()
			exit(1)
		tilt_low = _tmp_low
		tilt_high = _tmp_high
	else:
		tilt_low = servosystem_limits[1][0]
		tilt_high = servosystem_limits[1][1]
else:
	pan_low = servosystem_limits[0][0]
	pan_high = servosystem_limits[0][1]
	tilt_low = servosystem_limits[1][0]
	tilt_high = servosystem_limits[1][1]
pan_range = ( pan_high - pan_low )
best_pan = pan_low + pan_range/2
tilt_range = ( tilt_high - tilt_low )
best_tilt = tilt_low + tilt_range/2

lkScreenMsg("OK!\n")

lkScreenMsg(IndentLevel=0)
lkScreenMsg("___ EXECUTION ___")

# Set station speed and acceleration
lkScreenMsg("Setting speed and acceleration...", ToBeContinued=True, IndentLevel=1)
SSystem.SetStationSpeedAccel(station, arguments.speed_limit)
if SSystem.errCondition:
	lkScreenMsg(" FAILED!")
	lkScreenMsg(SSystem.lastError, IndentLevel=2)
	retvalue=1
else:
	lkScreenMsg(" OK!")
	( (_panspeed,_panaccel,) , (_tiltspeed, _tiltaccel,), ) = SSystem.GetStationSpeedAccel(station)
	lkScreenMsg("Pan Servo  --> \tSpeed: %s\t Acceleration: %s" % (
		[str(_panspeed),"unlimited"][_panspeed==0],
		[str(_panaccel),"unlimited"][_panaccel==0],
		),
		IndentLevel=2
	)
	lkScreenMsg("Tilt Servo --> \tSpeed: %s\t Acceleration: %s" % (
		[str(_tiltspeed),"unlimited"][_tiltspeed==0],
		[str(_tiltaccel),"unlimited"][_tiltaccel==0],
		)
	)


# Put antenna in initial position
(lastPanAngle,  lastTiltAngle) = SSystem.GetStationLastpos(station)
lkScreenMsg("Setting station target to its previous stored position ({pan},{tilt})... ".format(pan=lastPanAngle,tilt=lastTiltAngle), IndentLevel=1, ToBeContinued=True)
SSystem.SetStationPanTilt(station, lastPanAngle, lastTiltAngle, wait=True)
if SSystem.errCondition:
	lkScreenMsg(" FAILED!")
        lkScreenMsg("Exiting.", IndentLevel=1)
        SSystem.Close()
	exit(1)
else:
	lkScreenMsg(" OK!") 

# Start sniffing as a thread
lkScreenMsg("Start sniffing thread...", IndentLevel=1)
previous_nice = os.nice(0)
os.nice(40)
lkScreenMsg("Increased process nice from %d to %d to launch thread" % (previous_nice, os.nice(0)), IndentLevel=2)
thread_sniff = Thread(target=sniff_envelope)
thread_sniff.setDaemon(True)
thread_sniff.start()
lkScreenMsg("Sniffing thread started.")
os.nice(previous_nice-os.nice(0))
lkScreenMsg("Process nice re-established to %d" % os.nice(0))

lkScreenMsg("Acquiring beacon interval...", IndentLevel=1, ToBeContinued=True)
_accsleep = 0
while beacon_interval is None and _accsleep < 10:
	time.sleep(1)
	_accsleep += 1
if _accsleep >= 10:
	lkScreenMsg(" FAILED!")
	lkScreenMsg("Timeout acquiring beacon interval! Exiting.", IndentLevel=2)
        SSystem.Close()
	exit(1)
else:
	lkScreenMsg(" OK!")
	lkScreenMsg("beacon interval: %d ms" % beacon_interval, IndentLevel=2)
	if arguments.measure_time:
		measure_time = arguments.measure_time
		_nbeaconsinmt = int(measure_time/(beacon_interval/1000.0))
	else:
		_nbeaconsinmt = MIN_BEACONS_PER_MT
		measure_time = (_nbeaconsinmt+1)*(beacon_interval/1000.0)
	lkScreenMsg("Measure time: {:.2f} seconds ({:d} beacons)".format(measure_time, _nbeaconsinmt), IndentLevel=2)
	if _nbeaconsinmt < MIN_BEACONS_PER_MT:
		lkScreenMsg("WARNING! You have set a measure time that will hold less than %d beacons. Results may not be acqurate." % MIN_BEACONS_PER_MT, IndentLevel=3)
		


# Find beam loop
lkScreenMsg(IndentLevel=1)
lkScreenMsg("FINDING LOOP")


has_changed = False
pan_finished = False
tilt_finished = False
prgretvalue = 0
best_positions = []
tied_up = 0
measure_here = measure_time

while not (pan_finished and tilt_finished):
	lkScreenMsg(IndentLevel=2)
	if len(best_positions) > 1:
		if tied_up > 3:
			lkScreenMsg("Reached max number of ties! We don't expected any further improvements.", IndentLevel=2)
			best_pan = sum([item[0] for item in best_positions]) / len(best_positions)
			best_tilt = sum([item[1] for item in best_positions]) / len(best_positions)
			lkScreenMsg("Best position (average) : ( %d , %d )." % (best_pan,best_tilt))
			break
		else:
			q_list = best_positions
			tied_up += 1
			measure_here = 4 * measure_time
			lkScreenMsg("Iteration (%d steps): (%s)" % (len(best_positions),str(best_positions)), IndentLevel=2)
	else:
		tied_up = 0
		measure_here = measure_time
		q_list = []
		pan_step=pan_range / (ngrid-1)
		tmppan = max(best_pan-(pan_range/2), pan_low)
		tmptilt = max(best_tilt-(tilt_range/2),tilt_low)
		tilt_step = tilt_range / (ngrid-1)
		while tmppan <= min(best_pan+(pan_range/2),pan_high):
			if pan_finished:
				tmppan=best_pan
			while tmptilt >= max(best_tilt-(tilt_range/2), tilt_low) and tmptilt <= min(best_tilt+(tilt_range/2), tilt_high):
				if tilt_finished:
					tmptilt=best_tilt
				q_list.append((tmppan, tmptilt))
				if tilt_finished:
					break
				tmptilt += tilt_step
			
			tmptilt -= tilt_step
			tilt_step = -tilt_step
		
			if pan_finished:
				break
			tmppan+=pan_step

		_itdesc = "Iteration ({steps} steps): ( ".format(steps=len(q_list))
		if (pan_finished):
			_itdesc += "{pan} , ".format(pan=best_pan)
		else:
			_itdesc += "[{minpan} .. {maxpan}] , ".format(minpan=max(best_pan-(pan_range/2), pan_low) ,maxpan=min(best_pan+(pan_range/2),pan_high))
		if (tilt_finished):
			_itdesc += "{tilt} )\n".format(tilt=best_tilt)
		else:
			_itdesc += "[{mintilt} .. {maxtilt}] )\n".format(mintilt= max(best_tilt-(tilt_range/2), tilt_low), maxtilt=min(best_tilt+(tilt_range/2), tilt_high))

		lkScreenMsg(_itdesc,IndentLevel=2)
		
	isLost = True
	best_positions = []
	has_changed = False
	for q in q_list:
		lkScreenMsg("Step on  ({pan},{tilt})\n".format(pan=q[0],tilt=q[1]), IndentLevel=3)
		lkScreenMsg("Setting antenna...", IndentLevel=4, ToBeContinued=True)
		SSystem.SetStationPanTilt(station, q[0], q[1], wait=True)
		if not SSystem.errCondition:
			lkScreenMsg("OK!")

			lkScreenMsg("Measuring here for {:.2} seconds... ".format(measure_here))
			reset_sniff_counters()
			time.sleep(measure_here)	
			if current_power_sum_pos == 0:
				lkScreenMsg("Result: 0. Measuring again... ")
				reset_sniff_counters()
				time.sleep(measure_time)	
			try:
				here_power_avg = current_power_sum / current_power_count
				isLost = False
			except ZeroDivisionError:
				lkScreenMsg("Result: 0")
				here_power_avg = 0
				continue

			lkScreenMsg("Avg: \t\t%d" % here_power_avg, IndentLevel=5)
			lkScreenMsg("Max: \t\t%d" % current_power_max)
			lkScreenMsg("Num Beacons: \t%d" % current_power_count)

			if is_this_measure_better() is None:
				lkScreenMsg("=== TIE MAX ===", IndentLevel=8)
				best_positions.append( (q[0], q[1]) )
				
			if is_this_measure_better() == True:
				lkScreenMsg("*** NEW MAX ***", IndentLevel=8)
				best_powermax = current_power_max
				best_powercount = current_power_count
				best_poweravg = here_power_avg
				has_changed = True
				best_positions = []
				best_positions.append( (q[0], q[1]) )
		else:
			lkScreenMsg(" FAILED! Exiting.")
			prgretvalue = 1
			break
			
	if prgretvalue != 0:
		break
	if isLost:
		lkScreenMsg("*** TARGET LOST ***")
		break

	if has_changed:
		if len(best_positions) == 1:
			best_pan = best_positions[0][0]
			best_tilt = best_positions[0][1]
			lkScreenMsg("==> Center changed to ({pan},{tilt})".format(pan=best_pan, tilt=best_tilt), IndentLevel=3)
		else:
			lkScreenMsg("==> The following %d positions are candidates:" % len(best_positions), IndentLevel=3)
			lkScreenMsg(str(best_positions))
			lkScreenMsg("We will measure again over them.")
	else:
		lkScreenMsg("==> Center NOT changed. Was: ({pan},{tilt})".format(pan=best_pan, tilt=best_tilt), IndentLevel=3)
	lkScreenMsg("Avg: \t\t%d" % best_poweravg, IndentLevel=8)
	lkScreenMsg("Max: \t\t%d" % best_powermax)
	lkScreenMsg("Num Beacons: \t%d" % best_powercount)

	if len(best_positions) <= 1:
			_currentSpeedAccel = SSystem.GetStationSpeedAccel(station)
			if not pan_finished:
				pan_range = pan_range / 2
				if pan_range < angle_hyst:
					pan_finished = True
					pan_range = angle_hyst
				if pan_range <= 20 and _currentSpeedAccel[0][1] != 0:
					_currentSpeedAccel[0][1] = 0
					lkScreenMsg("==> Changing PAN Acceleration to non-limited.")

			if not tilt_finished:
				tilt_range = tilt_range / 2
				if tilt_range < angle_hyst:
					tilt_finished = True
					tilt_range = angle_hyst
				if tilt_range <= 20 and _currentSpeedAccel[1][1] != 0:
					_currentSpeedAccel[1][1] = 0
					lkScreenMsg("==> Changing TILT Acceleration to non-limited.")
			if not pan_finished or not tilt_finished:
				SSystem.SetStationSpeedAccel(
					station, 
					(
					_currentSpeedAccel[0][0],
					_currentSpeedAccel[1][0]
					) ,
					(
					_currentSpeedAccel[0][1],
					_currentSpeedAccel[1][1]
					)
				)
				if SSystem.errCondition:
					lkScreenMsg(" FAILED! %s" % SSystem.lastError, IndentLevel=4)
				else:
					lkScreenMsg(" OK!")
			lkScreenMsg("==> Ranges changed to ({dpan},{dtilt})\n".format(dpan=pan_range, dtilt=tilt_range), IndentLevel=3)

	# Reset max values
	best_powersumpos = -200
	best_powercount = 0
	best_poweravg = -200
	best_powermax = -200
	lkScreenMsg("==> Max records cleared.", IndentLevel=3)
	# Stop if debug mode
	if arguments.debug_mode:
		try:
			lkScreenMsg("Press enter to continue", ToBeContinued=True, IndentLevel=2)
			input(" :")
		except SyntaxError:
			pass
		
if not isLost and prgretvalue == 0:
	lkScreenMsg(IndentLevel=2)
	lkScreenMsg("Moving antenna to final position: ({pan},{tilt}) ...".format(pan=best_pan, tilt=best_tilt), ToBeContinued=True)
	SSystem.SetStationPanTilt(station, best_pan, best_tilt, wait=True)
	if not SSystem.errCondition:
		lkScreenMsg(" OK!")
	else:
		lkScreenMsg(" FAILED!")
		prgretvalue=1

# Termination
lkScreenMsg(IndentLevel=0)
lkScreenMsg("___ TERMINATION ___")

lkScreenMsg("\tServos will remain active.")

lkScreenMsg("Closing Servocontroller connection...")
SSystem.Close()

lkScreenMsg("Exiting...")
exit(prgretvalue)
