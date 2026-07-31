#!/usr/bin/env python3
"""Loop E: generate narration per beat through ElevenLabs REST, measure true
duration, write voice_ms back into scenes.json, build master.wav."""
import json, os, subprocess, sys, time, urllib.request, wave

ROOT = "/workspaces/youtube/channels/unclaimed/episodes/episode-01"
VOICE_ID = "SAz9YHcvj6GT2YYXdXww"   # River - Relaxed, Neutral, Informative (US)
MODEL = "eleven_multilingual_v2"
SPEED = 0.7
KEY = os.environ["ELEVENLABS_API_KEY"]
OUT = f"{ROOT}/resources/voice"
os.makedirs(OUT, exist_ok=True)

sc = json.load(open(f"{ROOT}/resources/script/scenes.json"))
scenes = sc["scenes"]

def tts(text, path, attempt=1):
    body = json.dumps({
        "text": text,
        "model_id": MODEL,
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75,
                           "style": 0.0, "use_speaker_boost": True, "speed": SPEED},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            open(path, "wb").write(r.read())
        return True
    except Exception as e:
        if attempt < 3:
            time.sleep(3 * attempt)
            return tts(text, path, attempt + 1)
        print(f"  FAILED after {attempt}: {e}")
        return False

def wav_ms(p):
    w = wave.open(p)
    try:
        return int(round(w.getnframes() / w.getframerate() * 1000))
    finally:
        w.close()

report = []
for s in scenes:
    n = s["beat_index"]
    mp3 = f"/tmp/beat-{n:02d}.mp3"
    wav = f"{OUT}/{n:02d}.wav"
    if not tts(s["narration"], mp3):
        report.append({"beat": n, "status": "TTS_FAILED"})
        continue
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3,
                    "-ar", "44100", "-ac", "1", wav], check=True)
    ms = wav_ms(wav)
    s["voice_ms"] = ms
    window = s["duration_ms"]
    over = ms - window
    status = "OK"
    if over > 1500:
        status = "OVERRUN"
    report.append({"beat": n, "voice_ms": ms, "window_ms": window,
                   "headroom_ms": window - ms, "status": status})
    print(f"beat {n:02d}  {ms/1000:6.2f}s / {window/1000:.0f}s  {status}")

json.dump(sc, open(f"{ROOT}/resources/script/scenes.json", "w"), indent=2)

# master.wav: each beat padded out to its full window so voice sits on the grid
concat = "/tmp/voice_concat.txt"
parts = []
for s in scenes:
    n = s["beat_index"]
    src = f"{OUT}/{n:02d}.wav"
    if not os.path.exists(src):
        continue
    pad = f"/tmp/pad-{n:02d}.wav"
    dur = s["duration_ms"] / 1000
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-af", f"adelay=400|400,apad", "-t", str(dur),
                    "-ar", "44100", "-ac", "1", pad], check=True)
    parts.append(pad)
with open(concat, "w") as f:
    for p in parts:
        f.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", concat, "-c", "copy", f"{OUT}/master.wav"], check=True)

overruns = [r for r in report if r.get("status") == "OVERRUN"]
failed = [r for r in report if r.get("status") == "TTS_FAILED"]
total = wav_ms(f"{OUT}/master.wav")
print(f"\nmaster.wav = {total/1000:.2f}s  ({total/1000/60:.2f} min)")
print(f"overruns: {len(overruns)}  failures: {len(failed)}")
json.dump({"voice_id": VOICE_ID, "model": MODEL, "speed": SPEED,
           "engine": "elevenlabs_rest", "beats": report},
          open(f"{ROOT}/resources/qa/voice-report.json", "w"), indent=2)
