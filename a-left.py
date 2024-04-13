#! /usr/bin/python

import os

# Set /dev/gpiomem the correct permissions
os.system('sudo chown root.gpio /dev/gpiomem')
os.system('sudo chmod g+rw /dev/gpiomem')

# Set environment variable for audio device before importing pygame
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:0,0' # Check that the device number N is right (hw:N,0)!!!

import asyncio
import RPi.GPIO as GPIO
import pygame

# **** SOUND ****
pygame.mixer.init(buffer=2048, channels=2)
sound = '/home/vattu/Documents/rain/RainMetalRoof_L.mp3'

try:
    pygame.mixer.music.load(sound)
    print(sound, 'loaded')
except pygame.error:
    print('Failed to load sound:', sound)
    exit(1)

pygame.mixer.music.set_volume(0)
pygame.mixer.music.play(loops = -1)


# **** GLOBAL TASK VARIABLES ****
fade_task = None
fade_in_task = None
fade_out_task = None
fade_in_triggered = None
fade_out_triggered = None


# **** MAIN COROUTINE ****
async def main():
    asyncio.create_task(fade())
    while True:
       await asyncio.sleep(1) # to keep the main coroutine running

# **** FADE LOOP ****
async def fade():
    current_volume = pygame.mixer.music.get_volume()
    print('Fade happening...')
    while True:
        for i in range(int(current_volume) * 100, 0):
            pygame.mixer.music.set_volume(i/100)
            await asyncio.sleep(0.05)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pygame.mixer.quit()
