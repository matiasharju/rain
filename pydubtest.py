import os

# Set environment variable for audio device before importing pydub
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:2,0' # Check that the device number N is right (hw:N,0)!!!


from pydub import AudioSegment
from pydub.playback import play

backgroundMusic = AudioSegment.from_wav("sound1.wav")

# pan the audio 15% to the right
panned_right = backgroundMusic.pan(+1.0)

# pan the audio 50% to the left
panned_left = backgroundMusic.pan(-1.0)

#Play audio
while True:
    try:
        play(panned_right)
    except KeyboardInterrupt:  # To handle Ctrl+C to exit the loop
        break
