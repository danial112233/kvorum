"""Prepare a recording to send to «Кворум» (formerly «Наш чат») as a voice message.

Prints, one per line: `upload` (the file to upload as an asset), `name`,
`type` (the audio type for the file entry), `size` (bytes of the audio),
`enc b64` when the file had to be packed as text, `dur` (seconds) and
`peaks` (40 bars for the waveform, empty when unknown).

With ffmpeg it converts anything to WebM/Opus, which uploads as video/webm and
plays everywhere the chat runs. Without ffmpeg, webm and m4a go as they are and
the rest is packed as base64 text, the way the page itself does it.

    python3 voice.py prep ~/Desktop/memo.m4a <scratch dir>
"""
import array
import base64
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

BARS = 40
RATE = 8000
LIMIT = 15 * 1024 * 1024
DIGITS = "0123456789abcdefghijklmnopqrstuv"
BY_EXT = {"webm": "audio/webm", "m4a": "audio/mp4", "mp4": "audio/mp4", "ogg": "audio/ogg", "oga": "audio/ogg",
          "opus": "audio/ogg", "mp3": "audio/mpeg", "wav": "audio/wav", "aac": "audio/aac", "flac": "audio/flac",
          "amr": "audio/amr", "3gp": "audio/3gpp", "caf": "audio/x-caf", "aiff": "audio/aiff", "aif": "audio/aiff"}
NAME_EXT = {"audio/webm": "webm", "audio/mp4": "m4a", "audio/ogg": "ogg", "audio/mpeg": "mp3", "audio/wav": "wav",
            "audio/aac": "aac", "audio/flac": "flac", "audio/amr": "amr", "audio/3gpp": "3gp", "audio/x-caf": "caf",
            "audio/aiff": "aiff"}


def peaks_and_duration(src):
    """Decode to 8 kHz mono PCM; the page draws the same kind of bars."""
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    samples = array.array("h")
    samples.frombytes(pcm[: len(pcm) // 2 * 2])
    if sys.byteorder == "big":
        samples.byteswap()
    n = len(samples)
    if not n:
        return 0.0, ""
    bars = []
    for i in range(BARS):
        a, b = i * n // BARS, max(i * n // BARS + 1, (i + 1) * n // BARS)
        bars.append(max(abs(x) for x in samples[a:b]))
    top = max(bars)
    code = "".join(DIGITS[round(31 * (p / top) ** 0.5)] for p in bars) if top else ""
    return n / RATE, code


def main():
    if len(sys.argv) != 4 or sys.argv[1] != "prep":
        sys.exit("usage: voice.py prep <audio file> <scratch dir>")
    src = Path(sys.argv[2]).expanduser().resolve()
    out_dir = Path(sys.argv[3]).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        sys.exit("no such file: %s" % src)
    stamp = dt.datetime.now().strftime("%d.%m %H-%M")
    ext = src.suffix.lower().lstrip(".")
    have_ffmpeg = shutil.which("ffmpeg") is not None

    dur, peaks, enc = 0.0, "", ""
    if have_ffmpeg:
        audio = out_dir / (src.stem + ".voice.webm")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-c:a", "libopus", "-b:a", "32k",
                        str(audio)], check=True)
        atype = "audio/webm"
        upload = audio
        dur, peaks = peaks_and_duration(audio)
    else:
        atype = BY_EXT.get(ext, "")
        if not atype:
            sys.exit("unknown audio format .%s; install ffmpeg or send webm/m4a/mp3" % ext)
        audio = src
        if atype == "audio/webm":
            upload = src
        elif atype == "audio/mp4":
            upload = out_dir / (src.stem + ".voice.mp4")  # an .mp4 name makes the upload go in as video/mp4
            shutil.copyfile(src, upload)
        else:
            upload, enc = out_dir / (src.name + ".b64.txt"), "b64"
    size = audio.stat().st_size
    if size > LIMIT:
        sys.exit("the recording is larger than 15 MB; send a shorter one")
    if enc:
        upload.write_text(base64.b64encode(audio.read_bytes()).decode("ascii"), encoding="utf-8")

    print("upload", upload)
    print("name", "Голосовое %s.%s" % (stamp, NAME_EXT.get(atype, ext or "webm")))
    print("type", atype)
    print("size", size)
    if enc:
        print("enc", enc)
    print("dur", round(dur, 1))
    print("peaks", peaks)


if __name__ == "__main__":
    main()
