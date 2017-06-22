
import lcddriver
import subprocess
import time

display = lcddriver.lcd()

# Main body of code
try:
    while True:
        # Remember that your sentences can only be 16 characters long!
        ip = subprocess.check_output("ifconfig eth0 | grep 'inet ' | awk -F'[: ]+' '{ print $3 }'")
        display.lcd_display_string("Ip local", 1) # Write line of text to first line of display
        display.lcd_display_string(str(ip), 2) # Write line of text to second line of display                                    # Give time for the message to be read
        display.lcd_clear()                               # Clear the display of any data
        time.sleep(2)                                     # Give time for the message to be read

except: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    display.lcd_display_string("Not connected",1)
    display.lcd_clear()
