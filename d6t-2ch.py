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

omron_bus = 4             # CHANGE OMRON BUS HERE
#threshold_temp_up = 24.6  # above which sound starts to fade in
#threshold_marginal = 0.2  # substracted from temp_up, used for triggering fade out
threshold = 4.0             # how many celsius degrees above the reference temperature until triggered

# **** SOUND ****
pygame.init()
print (pygame.mixer.get_init())
time.sleep(5)

sound1 = pygame.mixer.Sound('/home/vattu/Documents/rain/rain_umbrella.mp3')

#pygame.mixer.music.play(loops = -1)
sound1.play(loops = -1)


# **** GLOBAL TASK VARIABLES ****
fade_task = None
fade_in_task = None
fade_out_task = None
fade_in_triggered = None
fade_out_triggered = None

# **** OMRON ****
i2c_bus = smbus.SMBus(omron_bus)
OMRON_1=0x0a 					# 7 bit I2C address of Omron MEMS Temp Sensor D6T-44L
OMRON_BUFFER_LENGTH=35				# Omron data buffer size
temperature_data=[0]*OMRON_BUFFER_LENGTH 	# initialize the temperature data list

# intialize the pigpio library and socket connection to the daemon (pigpiod)
pi = pigpio.pi()              # use defaults
version = pi.get_pigpio_version()
print ('PiGPIO version = '+str(version))
handle = pi.i2c_open(omron_bus, 0x0a) # open Omron D6T device at address 0x0a

# initialize the device based on Omron's appnote 1
result=i2c_bus.write_byte(OMRON_1,0x4c);

# acquire sensor temp
#(bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
#print('temperature_data length:', len(temperature_data))
#sensor_temp = (256 * temperature_data[1] + temperature_data[0]) * 0.1
#sensor_temp_formatted = "{:.1f}".format(sensor_temp) # format to fixed bymber of decimals
#print('Sensor temp:', sensor_temp_formatted)


# **** MAIN COROUTINE ****
async def main():
    asyncio.create_task(measure())
    while True:
        await asyncio.sleep(1) # to keep the main coroutine running

# **** MEASURE LOOP ****
async def measure():
    global fade_task, fade_in_task, fade_out_task, fade_in_triggered, fade_out_triggered, tP, tPF, tRef
    while True:
        # acquire temperature readings
        global temperature_data
        lock = asyncio.Lock()
        await lock.acquire()
        (bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
        tPTAT = (256 * temperature_data[1] + temperature_data[0])
        tP0 = (256 * temperature_data[3] + temperature_data[2])
        tP1 = (256 * temperature_data[5] + temperature_data[4])
        tP2 = (256 * temperature_data[7] + temperature_data[6])
        tP3 = (256 * temperature_data[9] + temperature_data[8])
        tP4 = (256 * temperature_data[11] + temperature_data[10])
        tP5 = (256 * temperature_data[13] + temperature_data[12])
        tP6 = (256 * temperature_data[15] + temperature_data[14])
        tP7 = (256 * temperature_data[17] + temperature_data[16])
        tP8 = (256 * temperature_data[19] + temperature_data[18])
        tP9 = (256 * temperature_data[21] + temperature_data[20])
        tP10 = (256 * temperature_data[23] + temperature_data[22])
        tP11 = (256 * temperature_data[25] + temperature_data[24])
        tP12 = (256 * temperature_data[27] + temperature_data[26])
        tP13 = (256 * temperature_data[29] + temperature_data[28])
        tP14 = (256 * temperature_data[31] + temperature_data[30])
        tP15 = (256 * temperature_data[33] + temperature_data[32])
        tP = [tP0, tP1, tP2, tP3, tP4, tP5, tP6, tP7, tP8, tP9, tP10, tP11, tP12, tP13, tP14, tP15]

        # measure reference temperature by averaging the 4 lowest values of all 16 pixels
        #sorted_tP = sorted(tP)                              # sort the list in ascending order
        #lowest_four = sorted_tP[:4]                         # take the 4 lowest values
        #tRef = sum(lowest_four) / len(lowest_four)          # calculate the average for reference temperature
        #print("Average of the 4 lowest values (tRef):", tRef)

        # choose the lowest value of all pixels for reference temperature
        # TODO: lock the value when values_over_threshold is true, release when false
        tRef = min(tP)
        tHi = max(tP)  # highest value of all pixels
        print('Sensor temp:', "{:.1f}".format(tPTAT * 0.1), 'LOWEST (tRef):', "{:.1f}".format(tRef * 0.1), 'HIGHEST:', "{:.1f}".format(tHi * 0.1))

        # format temperatures for printing
        tPF = []    # list of formatted temperatures
        for i in range(0, len(tP)):
            tPF.append("{:.1f}".format(tP[i] * 0.1))     # format to fixed number of decimals
#        measured_temp_formatted = "{:.1f}".format(measured_temp * 0.1) # format to fixed bymber of decimals
        print(tPF[0], tPF[1], tPF[2], tPF[3], tPF[4], tPF[5], tPF[6], tPF[7], tPF[8], tPF[9], tPF[10], tPF[11], tPF[12], tPF[13], tPF[14], tPF[15])

        lock.release()
        time.sleep(0.2)

        # Pixel layout of D6T-44L-06 (16ch)
        #  ----- ----- ----- -----
        # | P0  | P1  | P2  | P3  |
        #  ----- ----- ----- -----
        # | P4  | P5  | P6  | P7  |
        #  ----- ----- ----- -----
        # | P8  | P9  | P10 | P11 |
        #  ----- ----- ----- -----
        # | P12 | P13 | P14 | P15 |
        #  ----- ----- ----- -----

        # check if any of the temperatures in the selected pixel combination (tS) is above the threshold
        #tS = tP                                 # all pixels
        tS = [tP[5], tP[6], tP[9], tP[10]]     # four innermost pixels
        values_over_threshold = [value for value in tS if value > tRef + (threshold *10)]
        if values_over_threshold:
            print("Temps over the threshold:", values_over_threshold)
        else:
            print("No temps are over the threshold")


#        if measured_temp >= (threshold_temp_up * 10) and not fade_in_triggered:
#        if measured_temp >= (threshold_temp_up * 10) and not fade_task in asyncio.all_tasks():
        if values_over_threshold and not fade_in_triggered:
#            print('Start sound, temp:', measured_temp, 'Threshold:', threshold_temp_up)
#            fade_task = asyncio.create_task(fade)
            pygame.mixer.music.set_volume(1)
            fade_in_triggered = True
            fade_out_triggered = False
#        elif measured_temp < ((threshold_temp_up - threshold_marginal) * 10) and not fade_out_triggered:
        elif not values_over_threshold and not fade_out_triggered:
#            print('Stop sound, temp:', measured_temp_formatted, 'Threshold:', threshold_temp_up)
#            asyncio.create_task(fade_out())
            pygame.mixer.music.set_volume(0)
            fade_in_triggered = False
            fade_out_triggered = True


# **** FADE LOOP ****
#async def fade():
#    current_volume = pygame.mixer.music.get_volume()
#    print('Fade happening...')
#    while (fade_in_triggered):
#        for i in range(int(current_volume) * 100, 100):
#            pygame.mixer.music.set_volume(i/100)
#            await asyncio.sleep(0.05)
#    while (fade_out_triggered):
#        for i in range(int(current_volume) * 100, 0):
#            pygame.mixer.music.set_volume(i/100)
#            await asyncio.sleep(0.05

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pygame.mixer.quit()
    pi.i2c_close(handle)
    pi.stop()
