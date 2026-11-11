"""台本（episodes/<日付>-<言語>.json）を VOICEVOX コアで読み上げて、音声とタイミングを作る。

  audio/<日付>-<言語>.mp3 を書き、台本に seconds / lines_timed / segments / made_at を書き込み、
  episodes.json（回の一覧）にこの回を足す。
  文ごとに合成して無音でつなぐので、lines_timed は合成結果そのものの秒になる（声とずれない）。

usage: python3 tools/voice.py EPISODE_JSON [--check] [--style N] [--speed X]
  --check  合成せず、各文の読み（カナ）だけを表示する。読み間違いは、台本の say を直す
  --style  VOICEVOX のスタイル ID、--speed 話す速さ（どちらも既定は station.json の voice）
先に tools/setup_voice.sh を実行しておく（道具は VV_HOME、既定 ~/.cache/myradio-voice）。ffmpeg が要る。

読み上げ用の文（say）の決まり：
  ・英字の名前はカタカナで書く（Gemini → ジェミニ）。数字は読みどおりに（5.2 → ごーてんに）
  ・「、」「。」は間を置く。「・」は間を置かない語の区切り（ジェミニ・フォー・カーボン）。
    区切らずに続けて書くと 1 語として平板に読まれるので、名前の中の語は「・」で分ける
"""
import datetime, io, json, os, subprocess, sys, wave, zoneinfo
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile

LEAD, LINE_GAP, PART_GAP, TAIL = 0.6, 0.25, 1.05, 2.05   # お手本の局（ものラジオ）と同じ間
ORT = "1.23.2"
STATION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def synthesizer(model):
    home = os.environ.get("VV_HOME") or os.path.expanduser("~/.cache/myradio-voice")
    syn = Synthesizer(Onnxruntime.load_once(filename=f"{home}/ort/lib/libvoicevox_onnxruntime.so.{ORT}"),
                      OpenJtalk(f"{home}/open_jtalk_dic_utf_8-1.11"))
    with VoiceModelFile.open(f"{home}/vvms/{model}.vvm") as m:
        syn.load_voice_model(m)
    return syn


def make_query(syn, say, style):
    """読み上げ用の文から AudioQuery を作る。「・」は「間を置かない区切り」として扱う
    （そのままだと「ジェミニ・フォー・カーボン」が 1 語ずつ途切れるため）。"""
    query = syn.create_audio_query(say, style)
    marks = [c for c in say.rstrip("、。・？！?!") if c in "、。・？！?!"]
    chunks = query.kana.split("、")
    if "・" not in marks or len(chunks) != len(marks) + 1:
        return query                                   # 対応が取れないときは、そのまま（間が入るだけ）
    kana = chunks[0] + "".join(("/" if m == "・" else "、") + c for m, c in zip(marks, chunks[1:]))
    return syn.create_audio_query_from_kana(kana, style)


def main():
    path = os.path.abspath(sys.argv[1])
    voice = json.load(open(os.path.join(STATION, "station.json"), encoding="utf-8")).get("voice", {})
    style = int(arg("--style", voice.get("style", 2)))
    speed = float(arg("--speed", voice.get("speed", 1.1)))
    ep = json.load(open(path, encoding="utf-8"))
    parts = [("opening", None, ep["opening"])] + [("news", i, n["lines"]) for i, n in enumerate(ep["news"])] \
        + [("closing", None, ep["closing"])]
    syn = synthesizer(voice.get("model", "0"))

    if "--check" in sys.argv:
        for _, _, lines in parts:
            for line in lines:
                print(make_query(syn, line["say"], style).kana)
        return

    rate, pcm = None, bytearray()
    timed, segments = [], []

    def silence(seconds):
        return bytes(2 * round(seconds * rate))

    def now():
        return len(pcm) / 2 / rate

    for p, (kind, index, lines) in enumerate(parts):
        seg_start = None
        for j, line in enumerate(lines):
            query = make_query(syn, line["say"], style)
            query.speed_scale = speed
            with wave.open(io.BytesIO(syn.synthesis(query, style))) as w:
                assert w.getnchannels() == 1 and w.getsampwidth() == 2
                if rate is None:
                    rate = w.getframerate()
                    pcm += silence(LEAD)
                frames = w.readframes(w.getnframes())
            start = now()
            if seg_start is None: seg_start = start
            pcm += frames
            timed.append({"start": round(start, 3), "end": round(now(), 3), "show": line["show"], "part": p})
            last = p == len(parts) - 1 and j == len(lines) - 1
            pcm += silence(TAIL if last else PART_GAP if j == len(lines) - 1 else LINE_GAP)
        segments.append({"kind": kind, "index": index, "start": round(seg_start, 3), "end": round(now(), 3)})

    total = now()
    name = os.path.splitext(os.path.basename(path))[0]            # <日付>-<言語>
    os.makedirs(os.path.join(STATION, "audio"), exist_ok=True)
    mp3 = os.path.join(STATION, "audio", name + ".mp3")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(bytes(pcm))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "wav", "-i", "pipe:0", "-ac", "1",
                    "-c:a", "libmp3lame", "-b:a", "64k", mp3], input=buf.getvalue(), check=True)

    ep["seconds"] = round(total, 2)
    ep["lines_timed"], ep["segments"] = timed, segments
    ep["made_at"] = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(ep, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 回の一覧（新しい順）
    lst = os.path.join(STATION, "episodes.json")
    eps = json.load(open(lst, encoding="utf-8")) if os.path.exists(lst) else []
    entry = next((e for e in eps if e["date"] == ep["date"]), None)
    if entry is None:
        entry = {"date": ep["date"]}; eps.append(entry)
    entry[ep["lang"]] = {"title": ep["title"], "seconds": ep["seconds"]}
    eps.sort(key=lambda e: e["date"], reverse=True)
    open(lst, "w", encoding="utf-8").write(json.dumps(eps, ensure_ascii=False) + "\n")
    print(f"{mp3}: {total:.2f}s, {len(timed)} lines, {os.path.getsize(mp3) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
