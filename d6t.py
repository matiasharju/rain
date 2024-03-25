#! /usr/bin/python

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
import pygame
import smbus
import sys
import getopt
import time
import pigpio

threshold_temp_up = 24.6  # above which sound starts to fade in
threshold_marginal = 0.2  # substracted from temp_up, used for triggering fade out

# **** SOUND ****
sound = '/home/vattu/Documents/rain/rain_umbrella.mp3'
pygame.mixer.init(buffer=512)

try:
    pygame.mixer.music.load(sound)
    print(sound, 'loaded')
except pygame.error:
    print('Failed to load sound:', sound)
    exit(1)

pygame.mixer.music.play(loops = -1)


# **** GLOBAL TASK VARIABLES ****
fade_in_task = None
fade_out_task = None
fade_in_triggered = None
fade_out_triggered = None


# **** OMRON ****
i2c_bus = smbus.SMBus(3)
OMRON_1=0x0a 					# 7 bit I2C address of Omron MEMS Temp Sensor D6T-44L
OMRON_BUFFER_LENGTH=5				# Omron data buffer size
temperature_data=[0]*OMRON_BUFFER_LENGTH 	# initialize the temperature data list

# intialize the pigpio library and socket connection to the daemon (pigpiod)
pi = pigpio.pi()              # use defaults
version = pi.get_pigpio_version()
print ('PiGPIO version = '+str(version))
handle = pi.i2c_open(3, 0x0a) # open Omron D6T device at address 0x0a on bus 1

# initialize the device based on Omron's appnote 1
result=i2c_bus.write_byte(OMRON_1,0x4c);

# acquire reference temp
(bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
reference_temp = (256 * temperature_data[1] + temperature_data[0]) * 0.1
reference_temp_formatted = "{:.1f}".format(reference_temp) # format to fixed bymber of decimals
print('Reference temp:', reference_temp_formatted)


# **** MEASURE LOOP ****
async def main():
    asyncio.create_task(measure())
    while True:
        await asyncio.sleep(1) # to keep the main coroutine running

async def measure():
    global fade_in_task, fade_out_task, fade_in_triggered, fade_out_triggered
    while True:
        # acquire temperature readings
        global temperature_data
        lock = asyncio.Lock()
        await lock.acquire()
        (bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
        measured_temp = (256 * temperature_data[3] + temperature_data[2])
        measured_temp_formatted = "{:.1f}".format(measured_temp * 0.1) # format to fixed bymber of decimals
        print('Temp:', measured_temp_formatted)
        lock.release()
        time.sleep(0.2)

        # compare temperatures
        if measured_temp >= (threshold_temp_up * 10) and not fade_in_triggered:
            print('Start sound, temp:', measured_temp, 'Threshold:', threshold_temp_up)
            asyncio.create_task(fade_in())
#            pygame.mixer.music.set_volume(1)
            fade_in_triggered = True
            fade_out_triggered = False
        elif measured_temp < ((threshold_temp_up - threshold_marginal) * 10) and not fade_out_triggered:
            print('Stop sound, temp:', measured_temp_formatted, 'Threshold:', threshold_temp_up)
            asyncio.create_task(fade_out())
#            pygame.mixer.music.set_volume(0)
            fade_in_triggered = False
            fade_out_triggered = True

async def fade_in():
    while True:
        current_volume = pygame.mixer.music.get_volume()
        print('Fade in')
        for i in range(int(current_volume) * 100, 100):
            pygame.mixer.music.set_volume(i/100)
            await asyncio.sleep(0.05)

async def fade_out():
    while True:
        current_volume = pygame.mixer.music.get_volume()
        print('Fade out')
        for i in range(int(current_volume) * 100, 0, -1):
            pygame.mixer.music.set_volume(i/100)
            await asyncio.sleep(0.05)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pygame.mixer.quit()
    pi.i2c_close(handle)
    pi.stop()
