
import lcddriver
import subprocess
import time

display = lcddriver.lcd()

# Main body of code
try:
    while True:
        
        ips = subprocess.check_output("hostname -I")#ifconfig eth0 | grep 'inet ' | awk -F'[: ]+' '{ print $3 }'", shell=True)
        for ip in ips.splitlines():
            
            display.lcd_display_string("Ip local", 1) 
            display.lcd_display_string(str(ip), 2) 
            time.sleep(2)
            display.lcd_clear()                               
                                                 

except: 
    display.lcd_display_string("Not connected",1)
    display.lcd_clear()
