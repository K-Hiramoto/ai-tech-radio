"""これまでの回で読んだニュースを一覧にする。ニュースを選ぶ前に見て、同じ話を選ばないようにする。

usage: python3 tools/recent.py [--days N]
  --days  何日前の回まで出すか（既定 7。日本時間の今日から数える）
回ごとに、名前（朝の回は <日付>、夕方の回は <日付>-pm）と題、ニュースごとの見出し・要点・出典の URL を出す。
"""
import datetime, glob, json, os, sys, zoneinfo

STATION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
today = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo")).date()
since = (today - datetime.timedelta(days=days)).isoformat()
names = (json.load(open(os.path.join(STATION, "station.json"), encoding="utf-8")).get("editions") or {})

eps = []
for path in glob.glob(os.path.join(STATION, "episodes", "*.json")):
    try: ep = json.load(open(path, encoding="utf-8"))
    except Exception: continue
    if isinstance(ep, dict) and ep.get("date", "") >= since and ep.get("lang", "ja") == "ja": eps.append(ep)
eps.sort(key=lambda e: (e["date"], e.get("edition") or ""), reverse=True)

print(f"直近 {days} 日（{since} 〜 {today.isoformat()}）の回：{len(eps)} 回、ニュース {sum(len(e.get('news', [])) for e in eps)} 本")
for ep in eps:
    eid = ep["date"] + ("-" + ep["edition"] if ep.get("edition") else "")
    label = names.get(ep.get("edition") or "", "")
    print(f"\n■ {eid}{'（' + label + '）' if label else ''}「{ep.get('title', '')}」")
    for n in ep.get("news", []):
        print(f"  ・{n.get('label', '')}：{' / '.join(n.get('points', []))}")
        print(f"    {n.get('url', '')}")
