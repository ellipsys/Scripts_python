
import lcddriver
import subprocess
import time

display = lcddriver.lcd()
try:
    display.lcd_clear()
    while True:
        ip = subprocess.check_output("ifconfig eth0 | grep 'inet ' | awk -F'[: ]+' '{ print $3 }'", shell=True)
        #for ip in ips.splitlines():#192.168.0.10
        if len(str(ip)) > 11:
            display.lcd_display_string("Ip local", 1) 
            display.lcd_display_string(str(ip), 2) 
            time.sleep(2)
            #display.lcd_clear()
        else: 
            ip = subprocess.check_output("ifconfig wlan0 | grep 'inet ' | awk -F'[: ]+' '{ print $3 }'", shell=True)
            display.lcd_display_string("Ip wlan0", 1) 
            display.lcd_display_string(str(ip), 2)                                      
            time.sleep(2)
            
except: 
    display.lcd_display_string("Not connected",1)
    
