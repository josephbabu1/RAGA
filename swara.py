import sounddevice as sd
import numpy as np
import librosa
# Settings
SAMPLE_RATE = 44100
CHUNK_SIZE = 2048
STABILITY_COUNT = 3
DEVICE = 1 # your Microphone Array
SWARA_NAMES = [
"Sa", "Ri1", "Ri2/Ga1", "Ga2/Ri3", "Ga3",
"Ma1", "Ma2", "Pa", "Da1", "Da2/Ni1", "Ni2/Da3", "Ni3"
]
def hz_to_swara(hz, sa_freq):
ratio = hz / sa_freq
semitones = round(12 * np.log2(ratio)) % 12
return SWARA_NAMES[semitones]
def get_pitch(chunk):
if np.max(np.abs(chunk)) < 0.01:
return None
pitches = librosa.yin(chunk, fmin=60, fmax=1000, sr=SAMPLE_RATE)
pitch = float(np.mean(pitches))
if pitch < 60 or pitch > 1000:
return None
return pitch
def record_chunk(duration_seconds):
samples = int(duration_seconds * SAMPLE_RATE)
recording = []
def callback(indata, frames, time, status):
recording.append(indata.copy())
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=’float32’,
blocksize=CHUNK_SIZE, device=DEVICE, callback=callback):
sd.sleep(int(duration_seconds * 1000))
if not recording:
return None
return np.concatenate(recording).flatten()
#--- Shruti Calibration--
print("Get ready to sing your Sa...")
print("Recording in 2 seconds. Hold your Sa steady for 3 seconds.")
sd.sleep(2000)
print("Sing now!")
sa_audio = record_chunk(3)
if sa_audio is None:
print("No audio captured. Check your microphone.")
exit()
sa_pitch = get_pitch(sa_audio)
if sa_pitch is None:
print("Couldn’t detect pitch. Sing louder and more clearly.")
exit()
print(f"Got it! Your Sa = {sa_pitch:.1f} Hz")
print("Now sing freely. Swara will appear below:\n")
#--- Real Time Loop--
buffer = []
last_printed = None
def callback(indata, frames, time, status):
global buffer, last_printed
chunk = indata.flatten()
pitch = get_pitch(chunk)
if pitch is None:
buffer = []
return
swara = hz_to_swara(pitch, sa_pitch)
buffer.append(swara)
if len(buffer) > STABILITY_COUNT:
buffer.pop(0)
if len(buffer) == STABILITY_COUNT and len(set(buffer)) == 1:
if swara != last_printed:
print(f" {swara}")
last_printed = swara
print("Press Ctrl+C to stop.\n")
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=’float32’,
blocksize=CHUNK_SIZE, device=DEVICE, callback=callback):
while True:
sd.sleep(100)
