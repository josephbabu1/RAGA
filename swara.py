import queue
import librosa
import numpy as np
import sounddevice as sd
SAMPLE_RATE = 44100
CHUNK_SIZE = 2048
DEVICE = 1
STABILITY_COUNT = 3
SILENCE_THRESHOLD = 0.01
FMIN, FMAX = 60, 1000
CALIBRATION_SECONDS = 3
SWARA_NAMES = [
    "Sa", "Ri1", "Ri2/Ga1", "Ga2/Ri3", "Ga3",
    "Ma1", "Ma2", "Pa", "Da1", "Da2/Ni1", "Ni2/Da3", "Ni3",
]
def get_pitch(audio):
    if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
        return None
    f0 = librosa.yin(audio, fmin=FMIN, fmax=FMAX, sr=SAMPLE_RATE, frame_length=CHUNK_SIZE)
    pitch = float(np.median(f0))
    return pitch if FMIN <= pitch <= FMAX else None
def hz_to_swara(hz, sa_freq):
    semitones = round(12 * np.log2(hz / sa_freq)) % 12
    return SWARA_NAMES[semitones]
def calibrate_sa():
    print("Get ready to sing your Sa...")
    print(f"Recording in 2 seconds. Hold your Sa steady for {CALIBRATION_SECONDS} seconds.")
    sd.sleep(2000)
    print("Sing now!")
    audio = sd.rec(int(CALIBRATION_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="float32", device=DEVICE)
    sd.wait()
    sa_pitch = get_pitch(audio.flatten())
    if sa_pitch is None:
        raise RuntimeError("Couldn't detect pitch. Sing louder and more clearly.")
    return sa_pitch
def run_realtime(sa_pitch):
    audio_q = queue.Queue()
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_q.put(indata.copy().flatten())
    recent = []
    last_printed = None
    print("Press Ctrl+C to stop.\n")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=CHUNK_SIZE, device=DEVICE, callback=callback):
        while True:
            pitch = get_pitch(audio_q.get())
            if pitch is None:
                recent.clear()
                last_printed = None
                continue
            recent.append(hz_to_swara(pitch, sa_pitch))
            recent = recent[-STABILITY_COUNT:]
            if len(recent) == STABILITY_COUNT and len(set(recent)) == 1:
                swara = recent[0]
                if swara != last_printed:
                    print(f"  {swara}")
                    last_printed = swara
def main():
    try:
        sa_pitch = calibrate_sa()
    except RuntimeError as e:
        print(e)
        return
    print(f"Got it! Your Sa = {sa_pitch:.1f} Hz")
    print("Now sing freely. Swara will appear below:\n")
    try:
        run_realtime(sa_pitch)
    except KeyboardInterrupt:
        print("\nStopped.")
if __name__ == "__main__":
    main()
