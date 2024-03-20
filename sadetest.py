import os

# Set environment variable for audio device before importing pygame
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:2,0' # Check that the device number N is right (hw:N,0)!!!

import asyncio
import time
import pygame

sound = '/home/vattu/Documents/rain/rain_umbrella.mp3'
pygame.mixer.init()

try:
    pygame.mixer.music.load(sound)
    print(sound, 'loaded')
except pygame.error:
    print('Failed to load sound:', sound)
    exit(1)

pygame.mixer.music.set_volume(100)
pygame.mixer.music.play(loops = -1)

try:
    while True:
        time.sleep(0.02)
except KeyboardInterrupt:
    pygame.mixer.quit()
