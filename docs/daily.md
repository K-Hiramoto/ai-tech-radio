# 毎朝の手順（AIテックラジオ）

この局の 1 回分を作って公開するまでの手順です。毎朝これを上から順に行います。JSON の形は [formats.md](formats.md)、局全体の決まりは [../AGENTS.md](../AGENTS.md)。

放送の日付は、日本時間の「今日」。扱うのは、きのうから今朝までに出た AI・テクノロジーのニュースです。

## 1. 準備

```sh
bash tools/setup_voice.sh     # 声の道具（VOICEVOX コア一式）。GitHub と PyPI から取る。数十秒
```

`episodes/<今日>-ja.json` がすでにあって、`episodes.json` にも載っていれば、今日の回は公開済みです。作り直さずに、5 の「公開の確認」へ進みます。

## 2. ニュースを選ぶ

- Web 検索で、きのうから今朝までの AI・テクノロジーのニュースを集める。英語と日本語の両方で探す（日次のまとめ記事が手がかりになる）
- **5 本**選ぶ。モデルや製品の公開、研究の成果、大きな提供開始や価格の変更を優先する。噂や未確認の報道、資金調達だけの話、政治の論評は後回し
- 直近 3 日の回（`episodes/`）で読んだ話は、新しい進展がなければ選ばない
- 選んだニュースは、**出典のページを実際に開いて**事実を確かめる。公式の発表を開けるときは公式を、開けないときは内容を確かめられた報道記事を出典にする
- 台本に書くのは、開いたページに書いてあることだけ。数字・日付・固有名詞は出典のとおりに。会社の発表による数字は「〜と発表」「〜だそうです」と伝聞で書く
- 出典のページから、リンクカード用に `og:title`、`og:image`（URL）、サイト名を控える。画像は保存しない（URL を書くだけ）。`og:image` がなければ `image` の欄を省く

## 3. 台本を書く

`episodes/<今日>-ja.json` を作る（前日の回を手本にする。`seconds`、`lines_timed`、`segments`、`made_at` は書かない。4 で入る）。

- `title`：いちばんのニュースを 25 字くらいまでで
- `opening`：2 文。「おはようございます、エーアイ・テックラジオです。◯月◯日、◯曜日の朝です。」と、今日の内容の予告
- `news`：5 本。それぞれ `label`（見出し）、`points`（要点 3 つ）、`details`（要点ごとの補足 3 つ）、`lines`（話す文 2 つ）、`url`（出典）、`link`（`url`、`title`、`site`、`image`）
- `closing`：2 文。今日の注目（`highlight` にその番号）と、「それでは今日も、いってらっしゃい。」
- 話す文は `{"say": 読み上げ用, "show": 字幕用}`。全体で 650〜750 字（say）、2 分弱が目安
- `say` の書き方は `tools/voice.py` の冒頭にある：英字の名前はカタカナ、数字は読みどおり、名前の中の語は「・」で区切る
- 口調は、ていねいで親しみのある話し言葉（「〜です」「〜なんです」「〜だそうです」）。意見や予想は足さない

## 4. 声を作って確かめる

```sh
python3 tools/voice.py episodes/<今日>-ja.json --check   # 読み（カナ）を見る。読み間違いがあれば say を直す
python3 tools/voice.py episodes/<今日>-ja.json           # audio/<今日>-ja.mp3 を作り、台本と episodes.json を更新
python3 tools/check.py episodes/<今日>-ja.json           # OK と出るまで直す
```

## 5. 公開する

この順に実行する：

```sh
# (1) 台本を main に push する
git add episodes episodes.json && git commit -m "<今日> <title>" && git push origin main

# (2) 前日までの音声を、公開中の gh-pages から audio/ に取ってくる（今日の mp3 はそのまま残る）
git fetch -q origin gh-pages && git archive FETCH_HEAD audio | tar -x

# (3) gh-pages を「main の中身＋直近 30 日の音声＋共有カード」で作り直して公開する
SHARE_FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc tools/publish.sh
```

- (2) を飛ばさない。作業する環境は毎回まっさらで、`publish.sh` は gh-pages を手元の `audio/` で作り直すので、飛ばすと過去の回の音声が消える
- 音声は main にコミットしない（`.gitignore` 済み）
- `SHARE_FONT` のフォントがなければ、Noto Sans JP を `https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf` から取って、その場所を渡す

**公開の確認**：`gh api repos/K-Hiramoto/ai-tech-radio/pages/builds/latest --jq .status` が `built` になるまで待つ（1〜2 分）。

公開される場所：

- 放送：`https://k-hiramoto.github.io/ai-tech-radio/#<今日>/ja`
- 共有用（SNS やチャットに貼るとカードが出る）：`https://k-hiramoto.github.io/ai-tech-radio/share/<今日>-ja.html`

## うまくいかないとき

- 出典を開けないニュースは使わない。5 本そろわなければ、確かめられた本数（3 本以上）で作る
- 声が作れない、push できないなど、公開まで行けなかったときは、台本だけでも main に push しておき、何ができなかったかを報告する
- 秘密の情報（キー、メールアドレス、通知先の ID など）を、このリポジトリのどのファイルにも書かない
