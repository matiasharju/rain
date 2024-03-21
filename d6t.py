import smbus
import time

# Define I2C bus number (for Raspberry Pi 3 Model A+, it's usually bus 1)
bus_number = 1

# Define sensor address
sensor_address = 0x0A

# Define registers for temperature data
temperature_register = 0x00
ambient_temperature_register = 0x02

# Create an instance of smbus for I2C communication
bus = smbus.SMBus(bus_number)

def read_temperature():
    # Read temperature data from the sensor
    data = bus.read_i2c_block_data(sensor_address, temperature_register, 4)

    # Combine the two bytes into a single integer
    temperature = (data[1] << 8) + data[0]

    # Convert to Celsius
    temperature = temperature / 10.0

    return temperature

def read_ambient_temperature():
    # Read ambient temperature data from the sensor
    data = bus.read_i2c_block_data(sensor_address, ambient_temperature_register, 2)

    # Combine the two bytes into a single integer
    ambient_temperature = (data[1] << 8) + data[0]

    # Convert to Celsius
    ambient_temperature = ambient_temperature / 10.0

    return ambient_temperature

try:
    while True:
        # Read temperature
        temperature = read_temperature()
        ambient_temperature = read_ambient_temperature()

        print("Object Temperature: {}°C".format(temperature))
        print("Ambient Temperature: {}°C".format(ambient_temperature))

        # Wait for some time before reading again
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program")
