import pygame
import pyaudio
import wave
import time

def play_sound(file, channel):
    chunk = 1024
    wf = wave.open(file, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=1,
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=channel)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

pygame.init()

# Define file names
sound1_file = "sound1.wav"
sound2_file = "sound2.wav"

# Load sounds
sound1 = pygame.mixer.Sound(sound1_file)
sound2 = pygame.mixer.Sound(sound2_file)

# Play sounds on separate channels
sound1_channel = 0  # Change this to your desired output channel index
sound2_channel = 1  # Change this to your desired output channel index

# Start playing sounds
play_sound(sound1_file, sound1_channel)
play_sound(sound2_file, sound2_channel)

# Add a delay to ensure sounds finish playing
time.sleep(max(sound1.get_length(), sound2.get_length()))

# Keep the program running until the user closes the window
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)

pygame.quit()
