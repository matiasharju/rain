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
#print 'write result = '+str(result)

#for x in range(0, len(temperature_data)):
   #print x
   # Read all data  tem
   #temperature_data[x]=i2c_bus.read_byte(OMRON_1)
(bytes_read, temperature_data) = pi.i2c_read_device(handle, len(temperature_data))

# Display data 
print ('Bytes read from Omron D6T: '+str(bytes_read))
print ('Data read from Omron D6T : ')
for x in range(bytes_read):
   print(temperature_data[x])
#print 'done'

pi.i2c_close(handle)
pi.stop()
