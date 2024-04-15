#! /usr/bin/python

import asyncio
import smbus
import time
import pigpio

# **** INITIALISE SENSOR ****
omron_bus = 2                               # I2C bus number
i2c_bus = smbus.SMBus(omron_bus)
OMRON_1=0x0a 					            # 7 bit I2C address of the sensor
OMRON_BUFFER_LENGTH=35			            # data buffer size
temperature_data=[0]*OMRON_BUFFER_LENGTH 	# initialise temperature data list

pi = pigpio.pi()
handle = pi.i2c_open(omron_bus, 0x0a)       # open sensor at address 0x0a

result=i2c_bus.write_byte(OMRON_1,0x4c);    # initialise sensor

# **** MAIN COROUTINE ****
async def main():
    asyncio.create_task(measure())
    while True:
        await asyncio.sleep(1)              # to keep the main coroutine running

# **** MEASURE LOOP ****
async def measure():
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

        # format internal temperature value to Celsius degrees and print
        print('Sensor temp:', "{:.1f}".format(tPTAT * 0.1))

        # format sensor 'pixel' values to Celsius degrees and print 
        tPF = []    # list of formatted temperatures
        for i in range(0, len(tP)):
            tPF.append("{:.1f}".format(tP[i] * 0.1))     # format to fixed number of decimals
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


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pi.i2c_close(handle)
    pi.stop()
