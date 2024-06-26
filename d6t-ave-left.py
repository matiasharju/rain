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
import smbus
import sys
import getopt
import time
import pigpio
import csv
from datetime import datetime
import config

omron_bus = 3              # Omron I2C bus
threshold = config.threshold

# **** SOUND ****
pygame.mixer.init(buffer=2048, channels=2)
if config.left == 'keski':
    sound = '/home/vattu/Documents/rain/KeskiL.mp3'
else:
    sound = '/home/vattu/Documents/rain/ReunaL.mp3'

try:
    pygame.mixer.music.load(sound)
    print(sound, 'loaded')
except pygame.error:
    print('Failed to load sound:', sound)
    exit(1)

#pygame.mixer.music.set_volume(0.05)  #test sound
pygame.mixer.music.set_volume(0.0)  #no test sound
pygame.mixer.music.play(loops = -1)

time.sleep(1)   #test sound for 1 second
pygame.mixer.music.set_volume(0.0)

# **** OMRON ****
i2c_bus = smbus.SMBus(omron_bus)
OMRON_1=0x0a 					    # 7 bit I2C address of Omron MEMS Temp Sensor D6T-44L
OMRON_BUFFER_LENGTH=35				# Omron data buffer size
temperature_data=[0]*OMRON_BUFFER_LENGTH 	# initialize the temperature data list

# intialize the pigpio library and socket connection to the daemon (pigpiod)
pi = pigpio.pi()              # use defaults
version = pi.get_pigpio_version()
print ('PiGPIO version = '+str(version))
handle = pi.i2c_open(omron_bus, 0x0a) # open Omron D6T device at address 0x0a

# initialize the device based on Omron's appnote 1
result=i2c_bus.write_byte(OMRON_1,0x4c);

# **** VARIABLES ****
last_record_time = time.time()
last_print_time = time.time()
tAverage = 17.6
tRecorded = 176
letFirstTempRecording = True

# **** MAIN COROUTINE ****
async def main():
    asyncio.create_task(measure())
    while True:
        await asyncio.sleep(1) # to keep the main coroutine running

# **** MEASURE LOOP ****
async def measure():
    global tPRaw, tP, tPF, tRef, last_record_time, pi, handle, letFirstTempRecording, last_print_time, tRecorded
    while True:
        # acquire temperature readings
        global temperature_data
        lock = asyncio.Lock()
        await lock.acquire()

#        # read data in chunks of 16 bytes, v.2
#        temperature_data = bytearray()  # Use bytearray to store binary data
#
#        while len(temperature_data) < OMRON_BUFFER_LENGTH:
#            remaining_bytes = OMRON_BUFFER_LENGTH - len(temperature_data)
#            chunk_size = min(16, remaining_bytes)
#            try:
#                (bytes_read, temperature_data_chunk) = pi.i2c_read_device(handle, chunk_size)
#                if bytes_read != chunk_size:
#                    print("Incomplete I2C read. Expected:", chunk_size, "bytes. Received:", bytes_read, "bytes.")
#                    continue
#                temperature_data.extend(temperature_data_chunk)
#            except Exception as e:
#                print("I2C read error:", e)
#                continue
        
        # read all data at once (causes incomplete reads)
        try:
            (bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
            if bytes_read != OMRON_BUFFER_LENGTH:
                print("L - Incomplete I2C read. Expected:", OMRON_BUFFER_LENGTH, "bytes. Received:", bytes_read, "bytes.")
                lock.release()            # Release the lock before continuing
                pi.i2c_close(handle)      # Close the I2C handle to avoid deadlock
                await asyncio.sleep(5.0)  # Delay before trying again to avoid busy waiting
                handle = pi.i2c_open(omron_bus, 0x0a)  # Reopen the I2C handle before retrying
                await asyncio.sleep(1.0)  # Delay before retrying to avoid busy waiting
                await lock.acquire()      # Reacquire the lock before retrying
                sys.exit(1)
            
        except Exception as e:
            print("L - I2C read error:", e)
            lock.release()              # Release the lock to avoid deadlock
            pi.i2c_close(handle)        # Close the I2C handle to avoid deadlock
            await asyncio.sleep(5.0)    # Delay before trying again to avoid busy waiting
            handle = pi.i2c_open(omron_bus, 0x0a)  # Reopen the I2C handle before retrying
            await asyncio.sleep(1.0)    # Delay before trying again to avoid busy waiting
            await lock.acquire()        # Reacquire the lock before retrying
            sys.exit(1)

#        (bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
        
        #        tPTAT = (256 * temperature_data[1] + temperature_data[0])
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

        # choose the lowest value of all pixels for reference temperature
        #tRef = min(tP)
        #tMax = max(tP)  # highest value of all pixels
        tRef = min(tP) if min(tP) < 430 else tRef
        tMax = max(tP) if max(tP) < 430 else tMax

        # format temperatures for printing
        tPF = []    # list of formatted temperatures
        for i in range(0, len(tP)):
            tPF.append("{:.1f}".format(tP[i] * 0.1))     # format to fixed number of decimals
#        measured_temp_formatted = "{:.1f}".format(measured_temp * 0.1) # format to fixed bymber of decimals
#        print(tPF[0], tPF[1], tPF[2], tPF[3], tPF[4], tPF[5], tPF[6], tPF[7], tPF[8], tPF[9], tPF[10], tPF[11], tPF[12], tPF[13], tPF[14], tPF[15])

        lock.release()
        time.sleep(0.05)
#        time.sleep(0.01)

        # Pixel layout of D6T-44L-06 (16ch)
        #  ----- ----- ----- -----
        # | P0  | P1  | P2  | P3  |
        #  ----- ----- ----- -----
        # | P4  | P5  | P6  | P7  |
        #  ----- ----- ----- -----
        # | P8  | P9  | P10 | P11 |
        #  ----- ----- ----- -----
        # | P12 | P13 | P14 | P15       |
        #  ----- ----- ----- -----

        current_time = time.time()

        # print temperatures every 5 seconds
        if current_time - last_print_time >= 5:
            #print('LEFT - MIN:', "{:.1f}".format(tRef * 0.1), f'AVE: {tAverage:.1f}', 'MAX:', "{:.1f}".format(tMax * 0.1), 'DIF:', "{:.1f}".format((tMax * 0.1) - tAverage), 'VOL:', pygame.mixer.music.get_volume())
            #print('L - MIN:', "{:.1f}".format(tRef * 0.1), f'AVE: {tAverage:.1f}', 'MAX:', "{:.1f}".format(tMax * 0.1), 'DIF:', "{:.1f}".format((tMax * 0.1) - tAverage))
            print('L - MIN:', "{:.1f}".format(tRef * 0.1), f'REC:', "{:.1f}".format(tRecorded * 0.1), 'MAX:', "{:.1f}".format(tMax * 0.1), 'DIF:', "{:.1f}".format((tMax - tRecorded) * 0.1))
            last_print_time = current_time

        # record reference temperature every minute
        if current_time - last_record_time >= 60 or letFirstTempRecording:
            letFirstTempRecording = False
            record_reference_temperature()
            #calculate_average_temperature()
            last_record_time = current_time
#        print(f'Average temperature: {tAverage:.2f}')

        # check if any of the temperatures in the selected pixel combination (tS) is above the threshold
        tS = tP                                 # all pixels
        #tS = [tP[5], tP[6], tP[9], tP[10]]     # four innermost pixels
        #tS = [tP[0], tP[1], tP[2], tP[4], tP[5], tP[6], tP[8], tP[9], tP[10]]
        #values_over_threshold = [value for value in tS if value > tRef + (threshold *10)]
        #values_over_threshold = [2000 > value for value in tS if value > (tAverage * 10) + (config.threshold *10)]
        #values_over_threshold = [2000 > value for value in tS if value > (tRecorded) + (config.threshold *10)]
        values_over_threshold = [value for value in tS if (value > (tRecorded) + (config.threshold * 10)) and (value < 2000)]

        if values_over_threshold:
            print("L - Temps over the threshold:", values_over_threshold)
#        else:
#            print("No temps are over the threshold")


        if values_over_threshold and pygame.mixer.music.get_volume() < 1.0:
#            print('Fade up happening...')
            current_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(current_volume + 0.05)
            await asyncio.sleep(0.01)

        elif not values_over_threshold and pygame.mixer.music.get_volume() > 0.0:
            if pygame.mixer.music.get_volume() > 0.1:
#                print('Fade down happening...')
                current_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(current_volume - 0.01)
#                await asyncio.sleep(0.01)
            elif pygame.mixer.music.get_volume() <= 0.1:
#                print('Slower fade down happening...')
                current_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(current_volume - 0.001)
#                await asyncio.sleep(0.01)
        
#        print('Volume:', pygame.mixer.music.get_volume())

# **** Record reference temperature ****
def record_reference_temperature():
    global tRecorded
    tRecorded = tRef
    print('L - Reference temperature recorded:', "{:.1f}".format(tRecorded * 0.1))

    # Get current timestamp
    #timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save temperature and timestamp to file
    #if tRef < 300:  # record only valid temperatures
        #with open('temperature_data_L.csv', 'a', newline='') as file:  # append new temperatures to the existing ones
    #    with open('temperature_data_L.csv', 'w', newline='') as file:   # overwrite the file with new temperatures
    #        writer = csv.writer(file)
    #        writer.writerow([timestamp, "{:.1f}".format(tRef * 0.1)])

# **** Calculate average temperature ****
def calculate_average_temperature():
    global tAverage

    total_temperature = 0
    num_readings = 0

    # Get the total number of lines in the file
    with open('temperature_data_L.csv', 'r', newline='') as file:
        total_lines = sum(1 for _ in file)

    # Determine the number of lines to read based on whether there are at least 180 lines
    num_lines_to_read = min(180, total_lines)

    # Read temperature data from file and calculate total temperature and number of readings
    with open('temperature_data_L.csv', 'r') as file:
#        reader = csv.reader(file)
#        for row in reader:
#            total_temperature += float(row[1])
#            num_readings += 1

        # Move the file pointer to the correct position to read the last 180 lines
        file.seek(max(0, total_lines - num_lines_to_read))

        # Read the last 180 measurements
        for line in file:
            row = line.strip().split(',')
            total_temperature += float(row[1])
            num_readings += 1 

#        for line in (file.readlines() [-180:]):
#            row = line.split(',')
#            total_temperature += float(row[1])
#            num_readings += 1

    # Calculate average temperature
    if num_readings > 0:
        tAverage = total_temperature / num_readings
        print(f'L - Average temperature calculated: {tAverage:.2f}')
    else:
        print('L - No average temperatures available')


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pygame.mixer.quit()
    pi.i2c_close(handle)
    pi.stop()
