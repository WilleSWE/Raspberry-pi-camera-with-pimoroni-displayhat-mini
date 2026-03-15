import time, sys, os, subprocess
from datetime import datetime
from displayhatmini import DisplayHATMini
from PIL import Image, ImageDraw
from picamera2 import Picamera2

hat = DisplayHATMini(None)
picam2 = Picamera2()
hat.set_led(0, 0, 0)

config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (320, 240)})
picam2.configure(config)
picam2.start()

MODES = ["Capture", "Library", "Settings"]
current_mode_index = 0 
zoom_level = 1.0
exposure_val = 0.0
is_saving = False
photo_dir = os.path.expanduser("~/Photos")
current_library_index = 0

def get_sys_info():
    temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8").replace("temp=", "")
    disk = subprocess.check_output("df -h / | awk 'NR==2 {print $4}'", shell=True).decode("utf-8").strip()
    return temp, disk

def update_zoom(direction):
    global zoom_level
    step = zoom_level * 0.1
    zoom_level -= step if direction == "in" else -step
    zoom_level = max(0.01, min(1.0, zoom_level))
    offset = (1.0 - zoom_level) / 2
    crop_box = (int(offset*3280), int(offset*2464), int(zoom_level*3280), int(zoom_level*2464))
    picam2.set_controls({"ScalerCrop": crop_box})

def get_photos():
    if not os.path.exists(photo_dir): return []
    files = [f for f in os.listdir(photo_dir) if f.endswith('.jpg')]
    return sorted(files, reverse=True)

try:
    while True:
        frame = picam2.capture_array()
        img = Image.fromarray(frame)
        img_rgb = Image.merge("RGB", (img.split()[2], img.split()[1], img.split()[0]))
        img_display = img_rgb.rotate(90)
        draw = ImageDraw.Draw(img_display)
        current_mode = MODES[current_mode_index]

        if current_mode == "Capture":
            metadata = picam2.capture_metadata()
            exp = round(metadata.get("ExposureTime", 0) / 1000, 1)
            draw.text((5, 50), f"EXP: {exp}ms", fill=(255, 255, 255))
            draw.text((285, 110), f"{round(1.0/zoom_level, 1)}x", fill=(255, 255, 255))
            
        elif current_mode == "Library":
            photos = get_photos()
            if photos:
                current_library_index = max(0, min(len(photos)-1, current_library_index))
                img_lib = Image.open(os.path.join(photo_dir, photos[current_library_index])).resize((240, 320))
                img_display.paste(img_lib, (0,0))
                draw = ImageDraw.Draw(img_display)
                draw.text((5, 210), f"DEL (A) | {current_library_index+1}/{len(photos)}", fill=(255, 0, 0))
            else:
                draw.rectangle((0, 40, 320, 240), fill=(0,0,0))
                draw.text((80, 120), "EMPTY LIBRARY", fill=(255, 255, 255))

        elif current_mode == "Settings":
            temp, disk = get_sys_info()
            draw.rectangle((0, 40, 320, 240), fill=(20, 20, 20))
            draw.text((40, 60),  "--- SYSTEM INFO ---", fill=(255, 255, 255))
            draw.text((40, 90),  f"CPU TEMP: {temp}", fill=(200, 200, 200))
            draw.text((40, 110), f"SD FREE:  {disk}", fill=(200, 200, 200))
            draw.text((40, 150), "--- EXPOSURE (X/Y) ---", fill=(255, 255, 255))
            draw.text((40, 180), f"EV COMP: {round(exposure_val, 1)}", fill=(0, 255, 0))

        for i, m in enumerate(MODES):
            color = (255, 255, 255) if i == current_mode_index else (100, 100, 100)
            draw.text((50 + (i * 80), 12), m.upper(), fill=color)
        
        sc = (255,0,0) if is_saving else ((0,0,255) if current_mode=="Library" else ((255,0,255) if current_mode=="Settings" else (0,255,0)))
        draw.ellipse((10, 10, 25, 25), fill=sc, outline=(255, 255, 255))

        hat.st7789.display(img_display)
        
        if hat.read_button(hat.BUTTON_B):
            current_mode_index = (current_mode_index + 1) % len(MODES)
            time.sleep(0.3); continue

        if current_mode == "Capture":
            if hat.read_button(hat.BUTTON_X): update_zoom("in"); time.sleep(0.05)
            if hat.read_button(hat.BUTTON_Y): update_zoom("out"); time.sleep(0.05)
            if hat.read_button(hat.BUTTON_A) and not is_saving:
                is_saving = True; hat.set_led(0, 1, 0)
                path = os.path.join(photo_dir, datetime.now().strftime("%Y%m%d-%H%M%S.jpg"))
                img_rgb.rotate(90, expand=True).save(path)
                time.sleep(0.2); hat.set_led(0, 0, 0); is_saving = False

        elif current_mode == "Library":
            if hat.read_button(hat.BUTTON_X): current_library_index -= 1; time.sleep(0.2)
            if hat.read_button(hat.BUTTON_Y): current_library_index += 1; time.sleep(0.2)
            if hat.read_button(hat.BUTTON_A):
                photos = get_photos()
                if photos: os.remove(os.path.join(photo_dir, photos[current_library_index])); hat.set_led(1, 0, 0); time.sleep(0.2); hat.set_led(0, 0, 0)

        elif current_mode == "Settings":
            if hat.read_button(hat.BUTTON_X): 
                exposure_val = min(4.0, exposure_val + 0.5)
                picam2.set_controls({"ExposureValue": exposure_val}); time.sleep(0.2)
            if hat.read_button(hat.BUTTON_Y): 
                exposure_val = max(-4.0, exposure_val - 0.5)
                picam2.set_controls({"ExposureValue": exposure_val}); time.sleep(0.2)

except KeyboardInterrupt:
    picam2.stop(); sys.exit()
