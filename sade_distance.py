import os

# Set /dev/gpiomem the correct permissions
os.system('sudo chown root.gpio /dev/gpiomem')
os.system('sudo chmod g+rw /dev/gpiomem')

# Set environment variable for audio device before importing pygame
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:2,0' # Check that the device number N is right (hw:N,0)!!!

import asyncio
import RPi.GPIO as GPIO
import time
import pygame

GPIO.setmode(GPIO.BCM)

TRIG = 4
ECHO = 17
distanceToFloor = 208
distanceMarginal = 10

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
print('Waiting for sensor to settle...')
time.sleep(2)
print('Sensor ready')

sound = 'rain_umbrella.mp3'
pygame.mixer.init()

try:
    pygame.mixer.music.load(sound)
    print(sound, 'loaded')
except pygame.error:
    print('Failed to load sound:', sound)
    exit(1)

pygame.mixer.music.play(loops = -1)

distances_buffer = []

# Global task variables
fade_in_task = None
fade_out_task = None

fade_in_triggered = False
fade_out_triggered = False

async def distance_measurement():
    global fade_in_task, fade_out_task, fade_in_triggered, fade_out_triggered
    while True:
        GPIO.output(TRIG, True)
#        await asyncio.sleep(0.00001)
        await asyncio.sleep(0.06)
        GPIO.output(TRIG, False)

        pulse_start = time.time()

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        if pulse_start is None or pulse_end is None:
            continue  # If we didn't get valid pulse times, skip this iteration

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150
        distance = round(distance, 2)
#        print('Distance:', distance, 'cm')

        distances_buffer.append(distance) # Add 5 latest measurements to buffer
        if len(distances_buffer) > 5:
            distances_buffer.pop(0)

        median_distance = sorted(distances_buffer)[len(distances_buffer) // 2] # Take the median measurement
        print('Median distance:', median_distance, 'cm - Actual distance:', distance, 'cm')

        if median_distance < (distanceToFloor-distanceMarginal) and not fade_in_triggered:
            fade_in_task = await fade_change_task(fade_in_task, audio_fade_in)
            fade_in_triggered = True
            fade_out_triggered = False
        elif median_distance >= (distanceToFloor-distanceMarginal) and median_distance < 300 and not fade_out_triggered:
            fade_out_task = await fade_change_task(fade_out_task, audio_fade_out)
            fade_out_triggered = True
            fade_in_triggered = False


async def fade_change_task(current_task, new_task_func):
    if current_task:
        current_task.cancel()
    return asyncio.create_task(new_task_func())

async def audio_fade_in():
#    if not pygame.mixer.music.get_busy():
#        pygame.mixer.music.play()
    print('Start fade in.')
    for i in range(0, 100):
        pygame.mixer.music.set_volume(i / 100)
        await asyncio.sleep(0.05)

async def audio_fade_out():
    print('Start fade out.')
    for i in range(100, 0, -1):
        pygame.mixer.music.set_volume(i / 100)
        await asyncio.sleep(0.05)
#    pygame.mixer.music.stop()

async def main():
    asyncio.create_task(distance_measurement())
    while True:
        await asyncio.sleep(1)  # Keep the main coroutine running

try:
    asyncio.run(main())
except KeyboardInterrupt:
    GPIO.cleanup()
    pygame.mixer.quit()
