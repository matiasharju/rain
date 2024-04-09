import os

# Set environment variable for audio device before importing pydub
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_SETDMIXRATE'] = '48000'
os.environ['SDL_ALSA_CARD'] = 'hw:2,0' # Check that the device number N is right (hw:N,0)!!!


from pydub import AudioSegment
from pydub.playback import play

sound1 = AudioSegment.from_wav("sound1.wav")
sound2 = AudioSegment.from_wav("sound2.wav")

# pan audio to the left
sound1Left = sound1.pan(-1.0)
# pan audio to the right
sound2Right = sound2.pan(+1.0)

#Play audio
while True:
    try:
        play(sound1Left)
        play(sound2Right)
    except KeyboardInterrupt:  # To handle Ctrl+C to exit the loop
        break
