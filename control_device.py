from subprocess import call
import subprocess
import os
# Set the volume to a specific level (0.0 to 1.0)
normal_volume = 50
ad_volume = 20

def set_screen_brightness(brightness):
    if brightness > 0.5:
        applescript = '''
        osascript -e 'tell application "System Events"' -e 'key code 144' -e ' end tell'
        '''
    else:
        applescript = '''
        osascript -e 'tell application "System Events"' -e 'key code 145' -e ' end tell'
        '''
    for i in range(0,5):
        call([applescript], shell=True)

def take_action(ad_confidence):
    if ad_confidence > 0.5:
        call(["osascript -e 'set volume output volume 30'"], shell=True)
        set_screen_brightness(0.3)
    else:
        call(["osascript -e 'set volume output volume 80'"], shell=True)
        set_screen_brightness(0.8)