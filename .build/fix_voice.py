#!/usr/bin/env python3
"""Adaptive second pass for Loop E. Any beat whose measured take does not fit
inside its window (allowing the 400ms lead-in used in the master) is
regenerated at a computed delivery speed. The narration is never trimmed --
the script already satisfies the 31-34 word budget, so pace is the variable."""
import json, os, subprocess, time, urllib.request, wave

ROOT = "/workspaces/youtube/channels/unclaimed/episodes/episode-01"
VOICE_ID = "SAz9YHcvj6GT2YYXdXww"
MODEL = "eleven_multilingual_v2"
BASE_SPEED = 0.7
LEAD_MS = 400
KEY = os.environ["ELEVENLABS_API_KEY"]
OUT = f"{ROOT}/resources/voice"

sc = json.load(open(f"{ROOT}/resources/script/scenes.json"))

def tts(text, path, speed, attempt=1):
    body = json.dumps({
        "text": text, "model_id": MODEL,
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75,
                           "style": 0.0, "use_speaker_boost": True,
                           "speed": round(speed, 3)},
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
            return tts(text, path, speed, attempt + 1)
        print(f"  FAILED: {e}")
        return False

def wav_ms(p):
    w = wave.open(p)
    try:
        return int(round(w.getnframes() / w.getframerate() * 1000))
    finally:
        w.close()

edits = []
for s in sc["scenes"]:
    n = s["beat_index"]
    wav = f"{OUT}/{n:02d}.wav"
    budget = s["duration_ms"] - LEAD_MS - 200      # hard ceiling
    target = budget - 900                          # aim, leaves breathing room
    ms = s["voice_ms"]
    speed = BASE_SPEED
    tries = 0
    while ms > budget and tries < 3:
        tries += 1
        speed = min(1.15, round(BASE_SPEED * (ms / target), 3))
        mp3 = f"/tmp/refit-{n:02d}.mp3"
        if not tts(s["narration"], mp3, speed):
            break
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3,
                        "-ar", "44100", "-ac", "1", wav], check=True)
        new = wav_ms(wav)
        print(f"beat {n:02d}  {ms/1000:.2f}s -> {new/1000:.2f}s  (speed {speed}, try {tries})")
        ms = new
    if speed != BASE_SPEED:
        edits.append({"beat": n, "speed": speed, "final_ms": ms,
                      "window_ms": s["duration_ms"], "narration_trimmed": False})
    s["voice_ms"] = ms
    s["voice_speed"] = speed

json.dump(sc, open(f"{ROOT}/resources/script/scenes.json", "w"), indent=2)

# rebuild master on the 15s grid
parts = []
for s in sc["scenes"]:
    n = s["beat_index"]
    src = f"{OUT}/{n:02d}.wav"
    pad = f"/tmp/pad2-{n:02d}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-af", f"adelay={LEAD_MS}|{LEAD_MS},apad",
                    "-t", str(s["duration_ms"] / 1000),
                    "-ar", "44100", "-ac", "1", pad], check=True)
    parts.append(pad)
with open("/tmp/vc2.txt", "w") as f:
    for p in parts:
        f.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", "/tmp/vc2.txt", "-c", "copy", f"{OUT}/master.wav"], check=True)

bad = [s["beat_index"] for s in sc["scenes"]
       if s["voice_ms"] + LEAD_MS > s["duration_ms"]]
print(f"\nmaster.wav = {wav_ms(f'{OUT}/master.wav')/1000:.2f}s")
print(f"beats refitted: {len(edits)}   still not fitting: {bad or 'none'}")
json.dump(edits, open(f"{ROOT}/resources/qa/voice-refit.json", "w"), indent=2)
