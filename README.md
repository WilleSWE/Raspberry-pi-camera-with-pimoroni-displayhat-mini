# Raspberry-pi-camera-with-pimoroni-displayhat-mini
A pretty simple camera script for the raspberry pi zero 2WH.

Just print the case files out of whatever, i painted mine i some pretty cool colors.

Just install the python script and have it auto start with crontab or similar stuff.
Very simple project that uses the pimoroni display hat mini and camera module v2, i think the v3 could be compatible with some small changes but I don't own that sooo uh yeah, not my problem right now :D

* Quick note : I used the latest raspberry pi OS (64-bit), I don't know everything about raspberry Pi's but you could probably use your brain in some clever way to make this boot up quicker,
* Note 2 : I added a script in crontab to host a simple webserver on http://cam-pi.local:8080/

@reboot sleep 10 && /usr/bin/python3 /home/pi/test_display.py >> /home/pi/camera_log.txt 2>&1

@reboot cd /home/pi/Photos && python3 -m http.server 8080 

First line is just to boot up the script.

Second line is to host the server at http://cam-pi.local:8080/ 


<img width="2560" height="1440" alt="Raspberry Pi Zero 2 W with Textures" src="https://github.com/user-attachments/assets/b80d78ea-f111-471b-9145-2553e6effe5d" />


<img width="2560" height="1440" alt="Raspberry Pi Zero 2 W with Textures2" src="https://github.com/user-attachments/assets/a89c5b5f-8439-4c06-9294-7819dc939108" />
