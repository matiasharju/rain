import os

# Set /dev/gpiomem the correct permissions
os.system('sudo chown root.gpio /dev/gpiomem')
os.system('sudo chmod g+rw /dev/gpiomem')

# Set environment variable for audio device before importing pygame
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:1,0'

import RPi.GPIO as GPIO
import time
import pygame

GPIO.setmode(GPIO.BCM)

TRIG = 4
ECHO = 17
thresholdDistance = 2.0 # distance for person detection 

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
print 'Waiting for sensor to settle...'
time.sleep(2)
print 'Sensor ready'

sound = 'rain_umbrella.mp3'
pygame.mixer.init()
pygame.mixer.music.load(sound)

try:
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150

        distance = round(distance, 2) # or maybe: (distance + 1.15, 2) ?
        print ('Distance:', distance, 'cm')
        
        if distance < thresholdDistance and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
            print ('Start playback and fade-in of', sound)
            for i in range(0, 100):
                pygame.mixer.music.set_volume(i / 100)  # Fades in the audio
#                if GPIO.input(sensorPin) != 1:
#                    break                               # Interrupt fade-in if movement not detected anymore
                time.sleep(0.05)
        elif distance >= thresholdDistance and pygame.mixer.music.get_busy():
            print ('Start fade-out')
            for i in range(100, 0, -1):
                pygame.mixer.music.set_volume(i / 100)  # Fades out the audio
#                if GPIO.input(sensorPin) == 1:
#                    break	                        # Interrupt fade-out if movement detected
                time.sleep(0.05)
            pygame.mixer.music.stop()
            print ('Audio stopped')

        time.sleep(0.02)

except KeyboardInterrupt:
    GPIO.cleanup()
    pygame.mixer.quit()
