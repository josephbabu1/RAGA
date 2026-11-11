Carnatic music is defined relative to a performer-chosen tonic (Sa), and raga
identity depends on swaras, arohanam and avarohanam sequences, phrases and
gamakas, making automated analysis difficult for tools built around absolute
Western pitch. This work presents RAGA ID, an explainable, DSP-based
software prototype that interprets live vocal or instrumental input in Carnatic
terms. The performer first provides Sa as the session reference. Audio is captured
at 44.1 kHz and processed in frames of 2048 samples (about 46 ms), where the
YIN algorithm estimates the fundamental frequency. Each estimate is converted
to a semitone position, round(12log2(f/Sa)), and mapped to one of 12 swara
positions. Loudness thresholding and consecutive-frame stability checks suppress
spurious readings during silence and transitions.
https://kattanchaya.netlify.app
