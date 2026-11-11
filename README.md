# AIテックラジオ

**AI・テクノロジーの、きのうの気になるニュースを、毎朝 2 分で。**

▶ 放送を聞く：https://k-hiramoto.github.io/ai-tech-radio/

キャラクターが毎朝ニュースを読む、HTML の番組です。再生位置に合わせてスライド・字幕・リンクカードが動き、見出しで飛べて、元の記事にすぐ行けます。台本はいつでも文字で読めます。

[myradio](https://github.com/monoradio102/myradio)（monoradio102 さん作）のテンプレートで開いた局です。

## この局のつくり

- **台本**：公開されている記事をもとに、AI（Claude）が毎朝書いています。ニュースごとに出典のリンクを付けています。AI が書いているので、誤りが含まれることがあります。大事なことは、出典の記事で確かめてください
- **声**：VOICEVOX:四国めたん（[VOICEVOX コア](https://github.com/VOICEVOX/voicevox_core)で合成）
- **キャスター**：myradio のお手本のキャラクター（AI で生成されたもの）
- **ニュースの画像**：記事のサイトが共有用に公開している画像（OGP）を、そのサイトから直接表示しています。保存や再配布はしていません

## 中身

```
station.json          局の自己紹介（名前・クレジット・声の設定）
index.html            プレーヤー（myradio のまま）
episodes.json         回の一覧
episodes/<日付>-ja.json  台本とタイミング
audio/<日付>-ja.mp3     声（main にはコミットしない。publish.sh が直近 30 日分だけ gh-pages に載せる）
character/            キャスター
tools/setup_voice.sh  声の道具（VOICEVOX コア一式）を用意する
tools/voice.py        台本を読み上げて、音声とタイミングを作る
tools/check.py        公開の前に、台本と音声を確かめる
tools/publish.sh      GitHub Pages への公開（myradio のまま）
tools/share.py        共有カード（myradio のまま）
docs/daily.md         毎朝の手順
docs/formats.md       JSON の形（myradio のまま）
```

毎朝の放送の作り方は [docs/daily.md](docs/daily.md) に書いてあります。

## ライセンスとクレジット

- プログラム（`index.html`、`tools/`）：MIT License（`index.html`、`tools/publish.sh`、`tools/share.py` は myradio のもの）
- 台本（`episodes/`、`episodes.json`）：CC0
- キャラ（`character/`）：myradio のお手本のキャラクター。使い方の条件は [myradio の README](https://github.com/monoradio102/myradio#ライセンス) に従います
- 声：VOICEVOX:四国めたん。[VOICEVOX 音声モデル 利用規約](https://github.com/VOICEVOX/voicevox_vvm)と、[四国めたんの音声ライブラリの利用規約](https://zunko.jp/con_ongen_kiyaku.html)に従います
