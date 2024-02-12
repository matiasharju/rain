import os

# Set environment variable for audio device before importing pygame
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:1,0'

import RPi.GPIO as GPIO
import time
import pygame

GPIO.setmode(GPIO.BCM)
sensorPin = 17
GPIO.setup(sensorPin, GPIO.IN)

sound = 'rain_umbrella.mp3'
pygame.mixer.init()
pygame.mixer.music.load(sound)

try:
    while True:
        if GPIO.input(sensorPin) == 1 and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
            print ('Start playback and fade-in of', sound)
            for i in range(0, 100):
                pygame.mixer.music.set_volume(i / 100)  # Fades in the audio
#                if GPIO.input(sensorPin) != 1:
#                    break                               # Interrupt fade-in if movement not detected anymore
                time.sleep(0.05)
        elif GPIO.input(sensorPin) != 1 and pygame.mixer.music.get_busy():
            print ('Start fade-out')
            for i in range(100, 0, -1):
                pygame.mixer.music.set_volume(i / 100)  # Fades out the audio
#                if GPIO.input(sensorPin) == 1:
#                    break	                        # Interrupt fade-out if movement detected
                time.sleep(0.05)
            pygame.mixer.music.stop()
            print ('Audio stopped')

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    pygame.mixer.quit()
