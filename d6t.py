#! /usr/bin/python

# A simple Python command line tool to control an Omron MEMS Temp Sensor D6T-44L
# By Greg Griffes http://yottametric.com
# GNU GPL V3 

# Jan 2015

import smbus
import sys
import getopt
import time 
import pigpio

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

# azquire reference temp
(bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
reference_temp = (256 * temperature_data[1] + temperature_data[0]) * 0.1
reference_temp_formatted = "{:.1f}".format(reference_temp) # format to fixed bymber of decimals
print('Reference temp:', reference_temp_formatted)


while True:
    # acquire temperature readings
    (bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))
    measured_temp = (256 * temperature_data[3] + temperature_data[2]) * 0.1
    measured_temp_formatted = "{:.1f}".format(measured_temp) # format to fixed bymber of decimals
    print('Temp:', measured_temp_formatted)
    time.sleep(0.2)


pi.i2c_close(handle)
pi.stop()
