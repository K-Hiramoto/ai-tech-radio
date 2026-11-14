# AIテックラジオ

**AI・テクノロジーの気になるニュースを、朝と夕方に 2 分ずつ。**

▶ 放送を聞く：https://k-hiramoto.github.io/ai-tech-radio/

キャラクターが毎日、朝（9 時）と夕方（17 時）にニュースを読む、HTML の番組です。夕方の回は、朝の回やそれまでの回で読んでいないニュースをお届けします。再生位置に合わせてスライド・字幕・リンクカードが動き、見出しで飛べて、元の記事にすぐ行けます。台本はいつでも文字で読めます。

[myradio](https://github.com/monoradio102/myradio)（monoradio102 さん作）のテンプレートで開いた局です。

## この局のつくり

- **台本**：公開されている記事をもとに、AI（Claude）が朝と夕方に書いています。ニュースごとに出典のリンクを付けています。AI が書いているので、誤りが含まれることがあります。大事なことは、出典の記事で確かめてください
- **声**：VOICEVOX:東北きりたん（[VOICEVOX コア](https://github.com/VOICEVOX/voicevox_core)で合成）
- **キャスター**：myradio のお手本のキャラクター（AI で生成されたもの）
- **ニュースの画像**：記事のサイトが共有用に公開している画像（OGP）を、そのサイトから直接表示しています。保存や再配布はしていません

## 中身

```
station.json          局の自己紹介（名前・クレジット・声の設定）
index.html            プレーヤー（myradio のものを、1 日 2 回の放送に対応させたもの）
episodes.json         回の一覧
episodes/<日付>-ja.json  朝の回の台本とタイミング（夕方の回は <日付>-pm-ja.json）
audio/<日付>-ja.mp3     朝の回の声（夕方の回は <日付>-pm-ja.mp3。main にはコミットしない。publish.sh が直近 30 日分だけ gh-pages に載せる）
character/            キャスター
tools/setup_voice.sh  声の道具（VOICEVOX コア一式）を用意する
tools/voice.py        台本を読み上げて、音声とタイミングを作る
tools/check.py        公開の前に、台本と音声を確かめる（前の回と同じ出典を使っていないかも）
tools/recent.py       これまでの回で読んだニュースの一覧（同じ話を選ばないために見る）
tools/publish.sh      GitHub Pages への公開（myradio のまま）
tools/share.py        共有カード（myradio のものを、1 日 2 回の放送に対応させたもの）
docs/daily.md         毎日の手順（朝の回・夕方の回）
docs/formats.md       JSON の形（myradio のものに、1 日 2 回の放送の決まりを足したもの）
```

朝と夕方の放送の作り方は [docs/daily.md](docs/daily.md) に書いてあります。

## ライセンスとクレジット

- プログラム（`index.html`、`tools/`）：MIT License（`index.html`、`tools/publish.sh`、`tools/share.py` は myradio のもの。`index.html` と `tools/share.py` には、この局で 1 日 2 回の放送に対応させる変更を入れています）
- 台本（`episodes/`、`episodes.json`）：CC0
- キャラ（`character/`）：myradio のお手本のキャラクター。使い方の条件は [myradio の README](https://github.com/monoradio102/myradio#ライセンス) に従います
- 声：VOICEVOX:東北きりたん。[VOICEVOX 音声モデル 利用規約](https://github.com/VOICEVOX/voicevox_vvm)と、[東北きりたんの音声ライブラリの利用規約](https://zunko.jp/con_ongen_kiyaku.html)に従います
