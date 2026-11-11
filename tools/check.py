"""公開の前に、1 回分の台本と音声を確かめる。問題があれば理由を表示して、終了コード 1 で終わる。

usage: python3 tools/check.py EPISODE_JSON
確かめること：必要な欄があるか、ニュースごとに出典 URL があるか、字幕（lines_timed）が台本の文と同じ並びか、
時刻が重なっていないか、パートの区切り（segments）が続いているか、音声の長さが台本の seconds と合うか、
回の一覧（episodes.json）に載っているか、台本に秘密らしい文字列がないか。
"""
import json, os, re, subprocess, sys

path = os.path.abspath(sys.argv[1])
station = os.path.dirname(os.path.dirname(path))
ep = json.load(open(path, encoding="utf-8"))
errors = []


def need(ok, message):
    if not ok: errors.append(message)


name = os.path.splitext(os.path.basename(path))[0]
for key in ("format", "date", "lang", "title", "opening", "news", "closing", "seconds", "lines_timed", "segments", "made_at"):
    need(key in ep, f"欄がない：{key}")
if not errors:
    need(name == f"{ep['date']}-{ep['lang']}", f"ファイル名と date / lang が合わない：{name}")
    need(1 <= len(ep["news"]) <= 8, f"ニュースの数：{len(ep['news'])}")
    for i, n in enumerate(ep["news"]):
        for key in ("label", "points", "lines", "url", "link"):
            need(n.get(key), f"news[{i}] に {key} がない")
        need(re.match(r"https://", n.get("url", "")), f"news[{i}] の出典 URL が https でない")
        need(n.get("link", {}).get("url"), f"news[{i}] の link.url がない")
        need("details" not in n or len(n["details"]) == len(n.get("points", [])), f"news[{i}] の details と points の数が違う")
    need(ep.get("highlight") is None or 0 <= ep["highlight"] < len(ep["news"]), "highlight が news の範囲にない")

    lines = ep["opening"] + [l for n in ep["news"] for l in n["lines"]] + ep["closing"]
    for l in lines:
        need(l.get("say") and l.get("show"), f"say / show がない文：{l}")
    lt, sg = ep["lines_timed"], ep["segments"]
    need([l["show"] for l in lines] == [l["show"] for l in lt], "lines_timed が台本の文と合わない（声を作り直す）")
    need(all(a["start"] < a["end"] for a in lt), "lines_timed に長さ 0 以下の文がある")
    need(all(a["end"] <= b["start"] for a, b in zip(lt, lt[1:])), "lines_timed の時刻が重なっている")
    need([s["kind"] for s in sg] == ["opening"] + ["news"] * len(ep["news"]) + ["closing"], "segments の並びが違う")
    need(all(abs(a["end"] - b["start"]) < 0.002 for a, b in zip(sg, sg[1:])), "segments がつながっていない")
    need(sg and abs(sg[-1]["end"] - ep["seconds"]) < 0.05, "segments の終わりと seconds が合わない")

    mp3 = os.path.join(station, "audio", name + ".mp3")
    if not os.path.exists(mp3):
        need(False, f"音声がない：{mp3}")
    else:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
                                   capture_output=True, text=True, check=True).stdout)
        need(abs(dur - ep["seconds"]) < 0.3, f"音声の長さ {dur:.2f}s と seconds {ep['seconds']} が合わない")

    eps = json.load(open(os.path.join(station, "episodes.json"), encoding="utf-8"))
    entry = next((e for e in eps if e["date"] == ep["date"]), {})
    need(entry.get(ep["lang"], {}).get("title") == ep["title"], "episodes.json にこの回がない（題が違う）")
    need(eps == sorted(eps, key=lambda e: e["date"], reverse=True), "episodes.json が新しい順でない")

    text = json.dumps(ep, ensure_ascii=False)
    need(not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|xox[abp]-|ghp_|sk-[A-Za-z0-9]{10}", text), "台本に、メールアドレスやキーらしい文字列がある")

if errors:
    print("\n".join("NG: " + e for e in errors)); sys.exit(1)
print(f"OK: {name}  {ep['seconds']}s  ニュース {len(ep['news'])} 本  「{ep['title']}」")
