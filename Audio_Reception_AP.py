#!/usr/bin/python
## lk_wifi_device_finder : A tool for finding (locating) Wi-Fi emitters
## PRERREQUISITES
## python-scapy python-pyaudio libasound2
##
## COMMENTS
##	(*) If you configure python-audio and alsa packages with its default values
##	then probably the initialization of alsa sound library will show some 
##	warning messages. This usually is not a problem, but is quite annoying. 
##	For that reason those messages have been suppressed. Please be aware that,
##	in order to do so, the code loads the libasound library manually to 
##	change the c_error_handler function. We assume that you have libasound2
##	installed, so we load 'libasound.so.2' file. If you have other version
##	of the library, then you should change this library name. This behaviour
##	and the adopted solution is documented here: 
##	http://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
##	If you don't have jackd installed, then you will also have warning
##	messages about "jack server" not being running, which might be avoided 
## 	by installing "jackd" (https://help.ubuntu.com/community/What%20is%20JACK)
##	(*)
###
### IMPORTS SECTION
###
import sys
from datetime import datetime
import time
from threading import Thread
from threading import Lock
import argparse
import fcntl, termios, struct
import pyaudio
from ctypes import *
# Import scapy while ignoring warnings (to avoid annoying warning msg about ipv6)
tmpout = sys.stdout; tmperr = sys.stderr
sys.stdout = open('/dev/null', 'w'); sys.stderr = open('/dev/null', 'w')
from scapy.all import *
sys.stdout = tmpout; sys.stderr = tmperr

### Global variables
min_power = -90
max_power = -10
min_tone = 500
max_tone = 2500
tone_length = 0.05
current_power_sum = 0
current_power_count = 0
must_print_timestamp = False
silent_mode = False

### Functions
def terminal_columns():
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w

def create_argumentparser():
    desc =  'lk_wifi_device_finder (v1.0) - Wi-Fi emitter finding tool\n'
    desc += 'Copyright (c) 2014 Layakk (www.layakk.com) (@layakk)'

    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    parser.add_argument("-i", "--interface", help='Interface to listen on (must be already up and in monitor mode', required=True)
    parser.add_argument("-r", "--refresh_interval", help='Refresh interval in miliseconds (default=400)', default=400)
    parser_mode_group = parser.add_mutually_exclusive_group(required=True)
    parser_mode_group.add_argument("-m", "--mac", help='MAC of the Wi-Fi device you are looking for', required=False)
    parser_mode_group.add_argument("-e", "--essid", help='ESSID of the Wi-Fi network you are looking for', required=False)
    parser.add_argument("-t", "--timestamp", help='Prints a timestamp every 5 seconds', required=False, action='store_true')
    parser.add_argument("-s", "--silent_mode", help='Turn off sound', required=False, action='store_true')
    parser.add_argument("-w", "--see_warnings", help='See library warnings', required=False, action='store_true')
    return parser


def process_args(args):

    global interface
    global refresh_interval_mseconds
    global target_mac
    global target_essid
    global must_print_timestamp
    global silent_mode

    interface = args.interface
    refresh_interval_mseconds = int(args.refresh_interval)
    if args.mac is not None:
    	target_mac = args.mac.lower()
	target_essid = None
    else:
    	target_mac = None
	target_essid = args.essid
    if args.timestamp:
	must_print_timestamp = True
    if args.silent_mode:
	silent_mode = True

def print_timestamp(interval_ms):
	sleep_sec = interval_ms / 1000.0
	while True:
		print datetime.now().strftime('### %d/%m/%Y %H:%M:%S')
        	time.sleep(sleep_sec)

def print_power(interval_ms):
	global min_power
	global max_power
	global current_power_sum
	global current_power_count
	global power_bar_width
	global min_tone
	global range_tone
	global tone_length
	global silent_mode

	sleep_sec = interval_ms / 1000.0
	while True:
		if current_power_count > 0:
			avg_power = current_power_sum / current_power_count
			if avg_power > max_power:
				avg_power = max_power
			if avg_power < min_power:
				avg_power = min_power
			power_pct = ( avg_power - min_power ) / float(range_power)
			numstr = "__[ %4d ]" %(avg_power)
			barstr = "_" * int ( power_pct * power_bar_width )
			this_freq = min_tone + ( power_pct * range_tone )
			if not silent_mode:
				play_tone(this_freq, 0.05)

			print numstr + barstr
			pow_mutex.acquire()
			current_power_sum = 0
			current_power_count = 0
			pow_mutex.release()
		else:
			print "__[      ]"
        	time.sleep(sleep_sec)
	

def sniffcb(p):
	global target_mac
	global target_essid
	global current_power_sum
	global current_power_count
	global parser_mode_group

        # Note:
	#     addr1 = receiver
	#     addr2 = transmitter
	#     addr3 = either original source or intended destination
	#     addr4 = original source when frame is both tx and rx on a wireless DS

	if p.haslayer(Dot11):
		if target_mac is not None:
        		p_mac  = p[Dot11].addr2
			if p_mac == target_mac:
				power = -(256-ord(p.notdecoded[-4:-3]))
				if power != -256:
					pow_mutex.acquire()
					current_power_sum += power
					current_power_count += 1
					pow_mutex.release()
		else:
			if p.haslayer(Dot11Beacon):
				try:
					if p.getlayer(Dot11Beacon).info == target_essid:
						power = -(256-ord(p.notdecoded[-4:-3]))
						pow_mutex.acquire()
						current_power_sum += power
						current_power_count += 1
						pow_mutex.release()
				except AttributeError:
					pass
			if p.haslayer(Dot11ProbeResp):
				try:
					if p.getlayer(Dot11ProbeResp).info == target_essid:
						power = -(256-ord(p.notdecoded[-4:-3]))
						pow_mutex.acquire()
						current_power_sum += power
						current_power_count += 1
						pow_mutex.release()
				except AttributeError:
					pass

# Ref.: http://askubuntu.com/questions/202355/how-to-play-a-fixed-frequency-sound-using-python
def play_tone(freq, duration):
	global BITRATE
	global audio
	global stream

	NUMBEROFFRAMES = int(BITRATE * duration)
	RESTFRAMES = NUMBEROFFRAMES % BITRATE
	WAVEDATA = ''

	for x in xrange(NUMBEROFFRAMES):
		WAVEDATA = WAVEDATA+chr(int(math.sin(x/((BITRATE/freq)/math.pi))*127+128))

	for x in xrange(RESTFRAMES):
		WAVEDATA = WAVEDATA+chr(128)
	
	stream.write(WAVEDATA)

#### Ref.: http://stackoverflow.com/questions/708672/pyaudio-working-but-spits-out-error-messages-each-time
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
	pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

	
### main

# Init some values and objects
pow_mutex = Lock()
range_power = ( max_power - min_power )
power_bar_width = terminal_columns() - 10 - 1
range_tone = max_tone - min_tone

# Process arguments
aparser = create_argumentparser()
args = aparser.parse_args()
process_args(args)

print "Initializing PyAudio..."
print "\t(Warning messages about server socket and jack server are normal and may be discarded)"
if not args.see_warnings:
	asound = cdll.LoadLibrary('libasound.so.2')
	# Set error handler
	asound.snd_lib_error_set_handler(c_error_handler)
audio = pyaudio.PyAudio()

print "\nStarting to measure. Press Ctrl-C to finish."
BITRATE = 16000
stream = audio.open(format = audio.get_format_from_width(1),
		channels = 1,
		rate = BITRATE,
		output = True)

# Timestamp thread
if must_print_timestamp == True:
	thread_timestamp = Thread(target=print_timestamp, args=(5000,))
	thread_timestamp.setDaemon(True)
	thread_timestamp.start()

# Start thread that prints out power measures
thread_power = Thread(target=print_power, args=(refresh_interval_mseconds,))
thread_power.setDaemon(True)
thread_power.start()

# Start sniffing
sniff(iface=interface, prn=sniffcb, store=0)

stream.stop_stream()
stream.close()
audio.terminate()
print "Audio device closed. Terminating.\n"
