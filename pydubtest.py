from pydub import AudioSegment
from pydub.playback import play

backgroundMusic = AudioSegment.from_wav("sound1.wav")

# pan the audio 15% to the right
panned_right = backgroundMusic.pan(+1.0)

# pan the audio 50% to the left
panned_left = backgroundMusic.pan(-1.0)

panned_right.export("panned_right.wav", format="wav")
panned_left.export("panned_left.wav", format="wav")

#Play audio
while True:
    try:
        play(panned_left)
    except KeyboardInterrupt:  # To handle Ctrl+C to exit the loop
        break
